import platform
import re
import time

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QPainter, QColor, QKeyEvent
from PyQt5.QtWidgets import QApplication, QWidget, QScrollArea, QMainWindow, QSizePolicy

from goddo_player.frame_in_out import FrameInOut
from goddo_player.state_store import StateStore, StateStoreSignals


class TimelineWidget2(QWidget):
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

    # def sizeHint(self) -> QtCore.QSize:
    #     return QSize(TimelineWidget2.INITIAL_WIDTH, self.get_height())

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # size_width = painter.fontMetrics().width('00:00')
        #
        # height_of_line = painter.fontMetrics().height()+5
        # painter.setPen(QColor(173, 202, 235))
        # for i in range(int(self.width()/self.WIDTH_OF_ONE_MIN)):
        #     x = (i+1)*self.WIDTH_OF_ONE_MIN
        #     painter.drawLine(x, height_of_line, x, self.get_height())
        #     painter.drawText(int(x-size_width/2), height_of_line-5, f"{i+1}:00")
        #
        #     for j in range(6):
        #         tick_x = int(x - self.WIDTH_OF_ONE_MIN/6*(j+1))
        #         tick_length = self.LENGTH_OF_TICK if j == 2 else int(self.LENGTH_OF_TICK / 2)
        #         painter.drawLine(tick_x, height_of_line, tick_x, height_of_line + tick_length)
        #
        # painter.drawLine(0, height_of_line, self.width(), height_of_line)

        # x = 0
        # for c in self.state.timeline['clips']:
        #     f: FrameInOut = c['frame_in_out']
        #     fps = self.state.preview_windows['source']['video_details']['fps']
        #     total_frames = self.state.preview_windows['source']['video_details']['total_frames']
        #     if f.out_frame and f.in_frame:
        #         n_frames = f.out_frame - f.in_frame
        #     elif f.in_frame:
        #         n_frames = total_frames - f.in_frame
        #     elif f.out_frame:
        #         n_frames = f.out_frame
        #     else:
        #         raise Exception("both in and out frame is blank")
        #     n_mins = n_frames / fps / 60
        #     width = n_mins * self.WIDTH_OF_ONE_MIN
        #     rect = QRect(x, height_of_line+50, width, 100)
        #     painter.fillRect(rect, Qt.darkRed)
        #     pen = painter.pen()
        #     painter.setPen(Qt.red)
        #     painter.drawRect(rect)
        #
        #     painter.setPen(Qt.white)
        #     filename = c["source"].fileName()
        #     painter.drawText(rect, Qt.TextWordWrap, f'{filename}\n{f.in_frame} - {f.out_frame}')
        #     painter.setPen(pen)
        #     x += width + 1

        painter.end()


class TimelineWindow2(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.setWindowTitle('当真ゆきが風俗嬢')
        self.setWindowTitle('美少女捜査官')
        self.resize(1075, 393)

        self.state = StateStore()

        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.scrollArea.setWidgetResizable(True)
        self.inner_widget = TimelineWidget2()
        self.inner_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.scrollArea.setWidget(self.inner_widget)
        self.scrollArea.setMinimumWidth(640)
        self.scrollArea.setMinimumHeight(360)
        self.setCentralWidget(self.scrollArea)

        print(f'{self.scrollArea.width()} x {self.scrollArea.height()}')

        self.setAcceptDrops(True)

    def resizeEvent(self, resize_event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(resize_event)
        self.inner_widget.resize(max(self.inner_widget.width(), resize_event.size().width()),
                                 resize_event.size().height())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_P:
            self.__process()
        else:
            super().keyPressEvent(event)

    def __process(self):
        import subprocess
        import os

        tmp_dir = os.path.join('..', '..', 'output', 'tmp')
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
        print(f'drag enter {event.mimeData().text()}')
        if re.fullmatch('^[0-9]*\\|[0-9]*$', event.mimeData().text()):
            event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        in_frame, out_frame = [int(x) if x != '' else None for x in event.mimeData().text().split('|')]
        self.state.add_timeline_clip_slot.emit({
            "source": self.state.preview_windows['source']['video_file'],
            "frame_in_out": FrameInOut(in_frame, out_frame),
        })
        self.activateWindow()
        self.update()
        print(f'preview {self.state.preview_windows}')
