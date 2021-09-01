from PyQt5 import QtCore
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QVBoxLayout, QLabel

from goddo_player.draw_utils import *
from goddo_player.time_frame_utils import *
from goddo_player.window_util import *


class TimelineWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, parent_window: QWindow):
        super().__init__()
        self.parent_window = parent_window

        print(parent_window.geometry())

        y = parent_window.geometry().bottom() + get_title_bar_height() + 10
        x = 10

        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()

        self.setGeometry(x, y, screen_rect.width()-20, screen_rect.bottom() - y - 10)

        layout = QVBoxLayout()
        # self.label = QLabel("Another Window")
        # layout.addWidget(self.label)
        self.setLayout(layout)

    def paintEvent(self, e):
        print('painting')
        painter = QPainter(self)

        brush = create_fill_in_brush(QColor(51, 51, 51))
        rect = QtCore.QRect(0, 0, painter.device().width(), painter
                            .device().height())
        painter.fillRect(rect, brush)

        regular_pen = create_pen(width=0.1, color=Qt.white)
        half_opacity_pen = create_pen(width=0.1, color=QColor(255,255,255,100))
        painter.setPen(regular_pen)
        # painter.setBrush(create_fill_in_brush(Qt.white))

        # painter.drawLine(QLine(self.geometry().left(), tick_bar_y, self.geometry().right(), tick_bar_y))
        height = 30
        painter.drawLine(0, height, self.geometry().width(), height)

        offset = 0
        tick_spacing = 10
        tick_height = 10
        num_of_ticks = int(self.geometry().width() / tick_spacing)
        for i in range(num_of_ticks):
            x = i*tick_spacing+offset
            if i % 10 == 0:
                cur_tick_height = height - tick_height * 1.5
            elif i % 5 == 0:
                cur_tick_height = height - tick_height
            else:
                cur_tick_height = height - tick_height / 2
            painter.setPen(regular_pen)
            painter.drawLine(x, height, x, cur_tick_height)

            if i % 10 == 0:
                painter.setPen(half_opacity_pen)
                painter.drawLine(x, height, x, self.geometry().height())

                painter.setPen(regular_pen)
                time_str = format_time(*ms_to_time_components(1000*60*i/10, 30))
                painter.drawText(QPoint(x, 10), time_str)

        scrollbar_height = 15
        painter.setPen(regular_pen)
        painter.drawRect(QRect(0, self.geometry().height()-scrollbar_height, self.geometry().width(), scrollbar_height))

        painter.setBrush(create_fill_in_brush(Qt.white))
        painter.drawRoundedRect(QRect(2, self.geometry().height() - scrollbar_height+2, 100, scrollbar_height-4), 5, 5)

        print(self.geometry())

    def mousePressEvent(self, event: QMouseEvent):
        print("mouse press")
        # self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        print("mouse move")
        self.update()

    def enterEvent(self, event: QtCore.QEvent):
        self.activateWindow()


