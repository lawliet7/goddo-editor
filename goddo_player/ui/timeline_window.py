from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QColor, QKeyEvent
from PyQt5.QtWidgets import QApplication, QWidget, QScrollArea, QMainWindow, QSizePolicy


class TimelineWidget(QWidget):
    INITIAL_WIDTH = 1000

    def __init__(self, get_height, scroll_area):
        super().__init__()
        self.get_height = get_height
        self.scroll_area = scroll_area

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(12, 29, 45))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def sizeHint(self) -> QtCore.QSize:
        print(f'in size hint {self.get_height()}')
        return QSize(TimelineWidget.INITIAL_WIDTH, self.get_height())

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size_width = painter.fontMetrics().width('00:00')

        width_of_one_min = 60
        height_of_line = painter.fontMetrics().height()+5
        painter.setPen(QColor(173, 202, 235))
        for i in range(int(self.width()/width_of_one_min)):
            x = (i+1)*width_of_one_min
            painter.drawLine(x, height_of_line, x, self.get_height())
            painter.drawText(int(x-size_width/2), height_of_line-5, f"{i+1}:00")

            for j in range(6):
                tick_x = int(x - width_of_one_min/6*(j+1))
                tick_length = 10 if j == 2 else 5
                painter.drawLine(tick_x, height_of_line, tick_x, height_of_line + tick_length)

        painter.drawLine(0, height_of_line, self.width(), height_of_line)

        painter.end()


class TimelineWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.scrollArea.setWidgetResizable(True)
        self.inner_widget = TimelineWidget(lambda: self.geometry().height(), self.scrollArea)
        self.inner_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.scrollArea.setWidget(self.inner_widget)
        # self.scrollArea.setMinimumWidth(640)
        # self.scrollArea.setMinimumHeight(360)
        self.setCentralWidget(self.scrollArea)

        print(f'{self.scrollArea.width()} x {self.scrollArea.height()}')

    def resizeEvent(self, resize_event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(resize_event)
        self.inner_widget.resize(max(self.inner_widget.width(), resize_event.size().width()), resize_event.size().height())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        else:
            super().keyPressEvent(event)


