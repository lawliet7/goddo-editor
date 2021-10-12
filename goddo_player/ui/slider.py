from PyQt5.QtCore import QObject, QPoint, QEvent, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QColor, QBrush, QPen

from goddo_player.ui.ui_component import UiComponent


class Slider(UiComponent):
    value_update_slot = pyqtSignal(float)

    def __init__(self, screen_update_fn, get_rect, initial_value=1):
        super().__init__()

        # self.slider_rect = None
        self.screen_update = screen_update_fn
        self.get_rect = get_rect
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
        print(f"paint slider {self.get_rect()}")

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
        print(f'slider mouse press {event.pos()} rect {self.get_rect()} self {self}')
        # if self.icon_rect.contains(event.pos()):
        #     # self.mute = not self.mute
        #     self.screen_update()
        if self.get_rect().contains(event.pos()):
            print(f'mouse press {event.pos()}')
            # self.volume = self.calc_volume_from_pos(event.pos().x())
            self.pos_pct = self.calc_pos_pct(event.pos().x())
            self.mouse_down = True
            self.screen_update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        # print('mouse release')
        if self.mouse_down:
            self.mouse_down = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # print('mouse move')
        if self.mouse_down:
            self.pos_pct = self.calc_pos_pct(event.pos().x())
            self.screen_update()

    def calc_pos_pct(self, x):
        pos = (x - self.get_rect().left()) / self.get_rect().width()
        return min(max(0, pos), 1)
