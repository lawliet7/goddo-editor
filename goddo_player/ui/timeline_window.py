import re

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QPainter, QColor, QKeyEvent
from PyQt5.QtWidgets import QApplication, QWidget, QScrollArea, QMainWindow, QSizePolicy

from goddo_player.ui.frame_in_out import FrameInOut
from goddo_player.ui.state_store import State


class TimelineWidget(QWidget):
    INITIAL_WIDTH = 1000
    WIDTH_OF_ONE_MIN = 60

    def __init__(self, get_height, scroll_area):
        super().__init__()
        self.get_height = get_height
        self.scroll_area = scroll_area

        self.state = State()
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(12, 29, 45))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.clips = []

    def sizeHint(self) -> QtCore.QSize:
        return QSize(TimelineWidget.INITIAL_WIDTH, self.get_height())

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size_width = painter.fontMetrics().width('00:00')

        height_of_line = painter.fontMetrics().height()+5
        painter.setPen(QColor(173, 202, 235))
        for i in range(int(self.width()/self.WIDTH_OF_ONE_MIN)):
            x = (i+1)*self.WIDTH_OF_ONE_MIN
            painter.drawLine(x, height_of_line, x, self.get_height())
            painter.drawText(int(x-size_width/2), height_of_line-5, f"{i+1}:00")

            for j in range(6):
                tick_x = int(x - self.WIDTH_OF_ONE_MIN/6*(j+1))
                tick_length = 10 if j == 2 else 5
                painter.drawLine(tick_x, height_of_line, tick_x, height_of_line + tick_length)

        painter.drawLine(0, height_of_line, self.width(), height_of_line)

        for c in self.clips:
            f: FrameInOut = c['frame_in_out']
            x = f.out_frame - f.in_frame
            fps = self.state.preview_windows['source']['video_details']['fps']
            n_mins = x / fps / 60
            width = n_mins * self.WIDTH_OF_ONE_MIN
            painter.fillRect(QRect(0, height_of_line+50, width, 100), Qt.darkRed)

        painter.end()


class TimelineWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('当真ゆきが風俗嬢')
        self.setGeometry(502, 457, 1075, 393)

        self.state = State()

        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.scrollArea.setWidgetResizable(True)
        self.inner_widget = TimelineWidget(lambda: self.geometry().height(), self.scrollArea)
        self.inner_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.scrollArea.setWidget(self.inner_widget)
        self.scrollArea.setMinimumWidth(640)
        self.scrollArea.setMinimumHeight(360)
        self.setCentralWidget(self.scrollArea)

        print(f'{self.scrollArea.width()} x {self.scrollArea.height()}')

        self.setAcceptDrops(True)

    def resizeEvent(self, resize_event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(resize_event)
        self.inner_widget.resize(max(self.inner_widget.width(), resize_event.size().width()), resize_event.size().height())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        print(f'drag enter {event.mimeData().text()}')
        if re.fullmatch('^[0-9]*\\|[0-9]*$', event.mimeData().text()):
            event.accept()

    # def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
    #     event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        # data = pickle.loads(event.mimeData().data("custom"))
        print('drop')
        in_frame, out_frame = [int(x) for x in event.mimeData().text().split('|')]
        print(f'drop {in_frame} {out_frame}')
        self.inner_widget.clips.append({
            "source": self.state.preview_windows['source']['video_file'],
            "frame_in_out": FrameInOut(in_frame, out_frame),
        })
        self.activateWindow()
        self.update()

