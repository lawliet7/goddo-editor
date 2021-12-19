import logging
import platform
import subprocess
import time

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QScrollArea, QMainWindow, QSizePolicy

from goddo_player.signals import StateStoreSignals
from goddo_player.state_store import StateStore, TimelineClip
from goddo_player.timeline_widget import TimelineWidget


class TimelineWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.setWindowTitle('当真ゆきが風俗嬢')
        self.setWindowTitle('美少女捜査官')
        self.resize(1075, 393)

        self.state = StateStore()
        self.signals = StateStoreSignals()

        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.scrollArea.setWidgetResizable(True)
        self.inner_widget = TimelineWidget()
        self.inner_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.scrollArea.setWidget(self.inner_widget)
        self.scrollArea.setMinimumWidth(640)
        self.scrollArea.setMinimumHeight(360)
        self.setCentralWidget(self.scrollArea)

        print(f'{self.scrollArea.width()} x {self.scrollArea.height()}')

        self.setAcceptDrops(True)
        self.setMouseTracking(True)

    def update(self):
        super().update()

        # scroll area widget resizable is not enabled so need to manually signal repaint
        self.inner_widget.update()

    def resizeEvent(self, resize_event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(resize_event)
        self.inner_widget.resize(max(self.inner_widget.width(), resize_event.size().width()),
                                 resize_event.size().height())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_P:
            self.__process()
        elif event.key() == Qt.Key_Delete:
            if self.inner_widget.selected_clip_index >= 0:
                print(f'delete {self.inner_widget.selected_clip_index}')
                # self.delete_selected_clip()
                print(self.updatesEnabled())
                self.signals.timeline_delete_selected_clip_slot.emit()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # super().mousePressEvent(event)

        logging.info('mouse press')

        for i, t in enumerate(self.inner_widget.clip_rects):
            _, rect = t
            if rect.contains(event.pos()):
                logging.info(f'{rect} found clip at index {i}')
                self.inner_widget.selected_clip_index = i
                self.inner_widget.update()
                return

        self.inner_widget.selected_clip_index = -1
        self.inner_widget.update()

    def add_rect_for_new_clip(self, clip: TimelineClip):
        self.inner_widget.add_rect_for_new_clip(clip)

    def __process(self):
        import os

        tmp_dir = os.path.join('', '..', 'output', 'tmp')
        from pathlib import Path
        Path(tmp_dir).mkdir(parents=True, exist_ok=True)
        for f in os.listdir(tmp_dir):
            os.remove(os.path.join(tmp_dir, f))

        for i, clip in enumerate(self.state.timeline.clips):
            start_time = clip.frame_in_out.in_frame / clip.fps
            end_time = clip.frame_in_out.out_frame / clip.fps
            file_path = clip.video_url.path()[1:] if platform.system() == 'Windows' else clip.video_url.path()
            output_path = os.path.join(tmp_dir, f'{i:04}.mp4')
            cmd = f"ffmpeg -ss {start_time:.3f} -i {file_path} -to {end_time - start_time:.3f} -cbr 15 {output_path}"
            logging.info(f'executing cmd: {cmd}')
            subprocess.call(cmd, shell=True)

            logging.info(f'{i} - {clip}')
            logging.info(f'{file_path} - {output_path} - {cmd}')

        concat_file_path = os.path.join(tmp_dir, 'concat.txt')
        tmp_vid_files = [f"file '{os.path.abspath(os.path.join(tmp_dir, f))}'\n" for f in os.listdir(tmp_dir)]
        with open(concat_file_path, mode='w', encoding='utf-8') as f:
            f.writelines(tmp_vid_files)
        logging.info('\n'.join(tmp_vid_files))

        output_file_path = os.path.join(tmp_dir, '..',  f'output_{time.time()}.mp4')
        cmd = f"ffmpeg -f concat -safe 0 -i {concat_file_path} -c copy {output_file_path}"
        logging.info(f'executing cmd: {cmd}')
        subprocess.call(cmd, shell=True)
        logging.info('output generated!!')

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().text() == 'source':
            event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        pw_state = self.state.preview_window
        clip = TimelineClip(pw_state.video_url, pw_state.fps, pw_state.total_frames, pw_state.frame_in_out)

        self.signals.add_timeline_clip_slot.emit(clip)
