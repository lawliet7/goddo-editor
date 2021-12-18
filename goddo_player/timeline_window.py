import logging
import typing

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QPainter, QColor, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget, QScrollArea, QMainWindow, QSizePolicy, QToolTip

from goddo_player.signals import StateStoreSignals
from goddo_player.state_store import StateStore, TimelineClip
from goddo_player.time_frame_utils import frames_to_time_components, build_time_str_least_chars, \
    build_time_ms_str_least_chars


class TimelineWidget(QWidget):
    INITIAL_WIDTH = 1000
    WIDTH_OF_ONE_MIN = 120
    LENGTH_OF_TICK = 20

    def __init__(self):
        super().__init__()
        # self.get_height = get_height
        # self.scroll_area = scroll_area

        # self.setWindowTitle('臥底女捜査官')
        # self.setWindowTitle('美少女捜査官')
        # self.setGeometry(600, 550, 1024, 360)

        self.state = StateStore()
        self.signals = StateStoreSignals()

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(12, 29, 45))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.clip_rects = []
        self.selected_clip_index = -1

        self.setMouseTracking(True)

    def sizeHint(self) -> QtCore.QSize:
        return QSize(TimelineWidget.INITIAL_WIDTH, 393)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        logging.info('painting')
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size_width = painter.fontMetrics().width('00:00')

        height_of_line = painter.fontMetrics().height()+5
        painter.setPen(QColor(173, 202, 235))
        for i in range(int(self.width()/self.WIDTH_OF_ONE_MIN)):
            x = (i+1)*self.WIDTH_OF_ONE_MIN
            painter.drawLine(x, height_of_line, x, 393)
            painter.drawText(int(x-size_width/2), height_of_line-5, f"{i+1}:00")

            for j in range(6):
                tick_x = int(x - self.WIDTH_OF_ONE_MIN/6*(j+1))
                tick_length = self.LENGTH_OF_TICK if j == 2 else int(self.LENGTH_OF_TICK / 2)
                painter.drawLine(tick_x, height_of_line, tick_x, height_of_line + tick_length)

        painter.drawLine(0, height_of_line, self.width(), height_of_line)

        x = 0
        for i, c in enumerate(self.state.timeline.clips):
            in_frame = c.frame_in_out.in_frame
            out_frame = c.frame_in_out.out_frame
            if out_frame and in_frame:
                n_frames = out_frame - in_frame
            elif in_frame:
                n_frames = c.total_frames - in_frame
            elif out_frame:
                n_frames = out_frame
            else:
                raise Exception("both in and out frame is blank")
            n_mins = n_frames / c.fps / 60
            width = n_mins * self.WIDTH_OF_ONE_MIN
            rect = QRect(x, height_of_line+50, width, 100)
            painter.fillRect(rect, Qt.darkRed)
            pen = painter.pen()
            if i == self.selected_clip_index:
                painter.setPen(Qt.green)
            else:
                painter.setPen(Qt.red)
            painter.drawRect(rect)
            # self.clip_rects.append((c, rect))

            painter.setPen(Qt.white)
            filename = c.video_url.fileName()
            in_frame_ts = build_time_str_least_chars(*frames_to_time_components(in_frame, c.fps))
            out_frame_ts = build_time_str_least_chars(*frames_to_time_components(out_frame, c.fps))
            painter.drawText(rect, Qt.TextWordWrap, f'{filename}\n{in_frame_ts} - {out_frame_ts}')
            painter.setPen(pen)
            x += width + 1

        painter.end()

    def mouseMoveEvent(self, event):
        for i, t in enumerate(self.clip_rects):
            c, rect = t
            if rect.contains(event.pos()):
                filename = c.video_url.fileName()
                in_frame_ts = build_time_str_least_chars(*frames_to_time_components(c.frame_in_out.in_frame, c.fps))
                out_frame_ts = build_time_str_least_chars(*frames_to_time_components(c.frame_in_out.out_frame, c.fps))
                duration = build_time_ms_str_least_chars(*frames_to_time_components(c.frame_in_out.out_frame - c.frame_in_out.in_frame, c.fps))
                msg = f'{filename}\n{in_frame_ts} - {out_frame_ts}\nduration: {duration}'
                QToolTip.showText(self.mapToGlobal(event.pos()), msg)
                return

        QToolTip.hideText()

    def add_rect_for_new_clip(self, clip: TimelineClip):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        height_of_line = painter.fontMetrics().height() + 5

        x = 0
        for c, rect in self.clip_rects:
            x += rect.width()

        in_frame = clip.frame_in_out.in_frame
        out_frame = clip.frame_in_out.out_frame
        if out_frame and in_frame:
            n_frames = out_frame - in_frame
        elif in_frame:
            n_frames = clip.total_frames - in_frame
        elif out_frame:
            n_frames = out_frame
        else:
            raise Exception("both in and out frame is blank")
        n_mins = n_frames / clip.fps / 60
        width = n_mins * self.WIDTH_OF_ONE_MIN
        rect = QRect(x, height_of_line + 50, width, 100)
        self.clip_rects.append((clip, rect))

        painter.end()


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

    # def delete_selected_clip(self):
    #     selected_idx = self.inner_widget.selected_clip_index
    #     clips = [x for i, x in enumerate(self.state.timeline.clips) if i != selected_idx]
    #     self.state.timeline.clips = []
    #     for c in clips:
    #         self.signals.add_timeline_clip_slot.emit(c)
    #     self.inner_widget.selected_clip_index = self.inner_widget.selected_clip_index if len(self.state.timeline.clips) > self.inner_widget.selected_clip_index else len(self.state.timeline.clips) - 1
    #     self.update()

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

        # for i, clip in enumerate(self.state.timeline['clips']):
        #     file = [x for x in self.state.files if x['file_path'] == clip['source'].path()][0]
        #     # print(self.state.files)
        #     print(file)
        #     print(clip)
        #     print(clip['source'].toLocalFile())
        #     frame_in_out: FrameInOut = clip['frame_in_out']
        #     start_time = frame_in_out.in_frame * file['fps'] / 1000
        #     end_time = frame_in_out.out_frame * file['fps'] / 1000
        #     file_path = file['file_path'][1:] if platform.system() == 'Windows' else file['file_path']
        #     output_path = os.path.join(tmp_dir, f'{i:04}.mp4')
        #     cmd = f"ffmpeg -ss {start_time} -i {file_path} -to {end_time - start_time} -cbr 15" \
        #           f" {output_path}"
        #     print(f'executing cmd: {cmd}')
        #     subprocess.call(cmd, shell=True)
        #
        # concat_file_path = os.path.join(tmp_dir, 'concat.txt')
        # tmp_vid_files = [f"file '{os.path.join(tmp_dir, f)}'\n" for f in os.listdir(tmp_dir)]
        # with open(concat_file_path, mode='w', encoding='utf-8') as f:
        #     f.writelines(tmp_vid_files)
        #
        # output_file_path = os.path.join(tmp_dir, '..',  f'output_{time.time()}.mp4')
        # cmd = f"ffmpeg -f concat -safe 0 -i {concat_file_path} -c copy {output_file_path}"
        # print(f'executing cmd: {cmd}')
        # subprocess.call(cmd, shell=True)

        print('output generated!!')

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().text() == 'source':
            event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        pw_state = self.state.preview_window
        clip = TimelineClip(pw_state.video_url, pw_state.fps, pw_state.total_frames, pw_state.frame_in_out)

        self.signals.add_timeline_clip_slot.emit(clip)
