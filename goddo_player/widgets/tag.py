from PyQt5 import QtCore
from PyQt5.QtCore import QRect, Qt, QPoint, QLine, QLineF
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QPen
from PyQt5.QtWidgets import QLabel, QFrame

from goddo_player.utils.draw_utils import draw_lines, set_pen_brush_before_paint


class TagWidget(QLabel):
    def __init__(self, text, delete_cb=None, tag_widget_height=25):
        super().__init__()

        self.setFixedHeight(tag_widget_height)
        self.baseTagColor = QColor(229, 246, 249)
        self.pen_for_x = QPen(QColor(8, 94, 185), 3, Qt.SolidLine, Qt.RoundCap)

        self.setText(text)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        rgb_str = f'rgb({self.baseTagColor.red()}, {self.baseTagColor.green()}, {self.baseTagColor.blue()})'
        self.setStyleSheet(f'background-color: {rgb_str};')
        self.setLineWidth(10)

        self.is_mouse_over = False

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        if self.is_mouse_over:
            painter = QPainter(self)

            length = 10
            right_margin = 3

            left = self.width() - right_margin - length
            right = self.width() - right_margin
            top = self.height() / 2 - length / 2
            bottom = self.height() / 2 + length / 2

            painter.fillRect(QRect(left, top, length, length), self.baseTagColor)

            lines_tuple = [
                (left, top, right, bottom),
                (left, bottom, right, top)
            ]
            draw_lines(painter, lines_tuple, pen=self.pen_for_x)

            painter.end()

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        super().enterEvent(a0)

        self.is_mouse_over = True
        self.update()

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        super().leaveEvent(a0)

        self.is_mouse_over = False
        self.update()





