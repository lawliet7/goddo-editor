from dataclasses import dataclass

from PyQt5 import QtGui
from PyQt5.QtCore import QRect, Qt, QEvent, QPoint
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QPen, QMouseEvent
from PyQt5.QtWidgets import QLabel, QFrame

from goddo_player.utils.draw_utils import draw_lines


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

        self.rect_coor = _RectCoordinate(self.width(), self.height(), 10, 3)

        self.delete_cb = delete_cb

    def initPainter(self, painter: QtGui.QPainter) -> None:
        super().initPainter(painter)

        # it gets resized after displaying text only, the one in init is completely wrong
        self.rect_coor = _RectCoordinate(self.width(), self.height(), 10, 3)

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        if self.is_mouse_over:
            painter = QPainter(self)

            painter.fillRect(self.rect_coor.to_rect(), self.baseTagColor)
            draw_lines(painter, self.rect_coor.get_lines(), pen=self.pen_for_x)

            painter.end()

    def enterEvent(self, event: QEvent) -> None:
        super().enterEvent(event)

        self.is_mouse_over = True
        self.update()

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)

        self.is_mouse_over = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)

        if self.rect_coor.is_in_rect(event.pos()):
            self.delete_cb(self.text())


@dataclass
class _RectCoordinate:
    tag_widget_width: int
    tag_widget_height: int
    length: int
    right_margin: int

    def __post_init__(self):
        self.left = self.tag_widget_width - self.right_margin - self.length
        self.right = self.tag_widget_width - self.right_margin
        self.top = self.tag_widget_height / 2 - self.length / 2
        self.bottom = self.tag_widget_height / 2 + self.length / 2

    def to_rect(self):
        return QRect(self.left, self.top, self.length, self.length)

    def get_lines(self):
        return [
            (self.left, self.top, self.right, self.bottom),
            (self.left, self.bottom, self.right, self.top)
        ]

    def is_in_rect(self, pt: QPoint):
        return self.left <= pt.x() <= self.right and self.top <= pt.y() <= self.bottom

