from PyQt5.QtCore import QPoint, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QColor, QBrush, QPen

from goddo_player.ui.ui_component import UiComponent


class Slider(UiComponent):
    value_update_slot = pyqtSignal(float)

    def __init__(self, parent, get_rect, initial_value=1):
        super().__init__(parent, get_rect)

        # self.slider_rect = None
        self.mouse_down = False
        self._pos_pct = initial_value

    @property
    def pos_pct(self):
        return self._pos_pct

    @pos_pct.setter
    def pos_pct(self, value):
        self._pos_pct = value
        self.value_update_slot.emit(value)

    def paint(self, painter, color=QColor('white')):
        # print(f"paint slider {self.get_rect()}")

        painter.setPen(QPen(color))

        # draw slider bar
        midpoint = int((self.get_rect().top() + self.get_rect().bottom()) / 2)
        painter.drawLine(
            QPoint(self.get_rect().left(), midpoint),
            QPoint(self.get_rect().right(), midpoint)
        )

        # draw circle on slider
        radius = 6
        x_pos = int(self.get_rect().width() * self.pos_pct + self.get_rect().left())
        painter.setBrush(QBrush(painter.pen().color()))
        painter.drawEllipse(QPoint(x_pos, self.get_rect().center().y() + 1), radius, radius)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.get_rect().contains(event.pos()):
            self.mouse_down = True
            self.pos_pct = self.calc_pos_pct(event.pos().x())
            self.window.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.mouse_down:
            self.mouse_down = False
            self.pos_pct = self.pos_pct
            self.window.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # print('mouse move')
        if self.mouse_down:
            self.pos_pct = self.calc_pos_pct(event.pos().x())
            self.window.update()

    def calc_pos_pct(self, x):
        pos = (x - self.get_rect().left()) / self.get_rect().width()
        return min(max(0, pos), 1)
