import math

from PyQt5.QtCore import QRect, Qt, QPoint, QEvent, QObject, pyqtSlot
from PyQt5.QtGui import QMouseEvent, QPen, QBrush, QPolygon, QFont, QColor

from goddo_player.ui.slider import Slider
from goddo_player.ui.ui_component import UiComponent


class VolumeControl(UiComponent):
    TEXT_WIDTH = 70
    SLIDER_WIDTH = 100
    ICON_WIDTH = 70

    def __init__(self, update_screen, get_rect):
        super().__init__()

        self.update_screen = update_screen
        self.get_rect = get_rect

        self.volume = 1
        self.text_rect: QRect = None
        self.volume_slider_rect: QRect = None
        self.volume_slider = Slider(self.update_screen, lambda: self.volume_slider_rect, initial_value=self.volume)
        self.volume_slider.value_update_slot.connect(self.volume_slider_update_handler)

        self.icon_rect: QRect = None
        self.play_rect: QRect = None
        self.mute = False
        self.mouse_down_volume = False

    @pyqtSlot(float)
    def volume_slider_update_handler(self, pct_pos):
        # print(f'pct pos {pct_pos}')
        self.volume = pct_pos

    def paint(self, painter, color=QColor("white")):
        # print(f"paint {self.get_rect()}")

        height = self.get_rect().height()
        top = self.get_rect().top()

        self.text_rect = QRect(self.get_rect().right() - VolumeControl.TEXT_WIDTH, top,
                               VolumeControl.TEXT_WIDTH, height)

        self.volume_slider_rect = QRect(self.text_rect.left() - VolumeControl.SLIDER_WIDTH, top,
                                        VolumeControl.SLIDER_WIDTH, height)

        self.icon_rect = QRect(self.volume_slider_rect.left() - VolumeControl.ICON_WIDTH, top + 5,
                               VolumeControl.ICON_WIDTH, height - 10)

        painter.setPen(QPen(color))

        font = QFont()
        font.setFamily("cursive")
        font.setPointSize(14)
        painter.setFont(font)
        volume = 0 if self.mute else round(self.volume*100)
        painter.drawText(QRect(self.text_rect.x()+10, self.text_rect.y()+6, self.text_rect.width()-25,
                               height),
                         Qt.AlignHCenter, str(volume))

        # draw icon
        painter.setPen(QPen(color))
        painter.setBrush(QBrush(color))
        len_of_side = math.sqrt(((self.icon_rect.height() * 0.6 / 2) ** 2) / 2)
        len_of_handle = len_of_side / 2
        icon_x = self.icon_rect.width() * 0.6 + self.icon_rect.left()
        painter.drawPolygon(QPolygon([
            QPoint(int(icon_x), int(self.icon_rect.top() + self.icon_rect.height() * 0.8)),  # right top
            QPoint(int(icon_x), int(self.icon_rect.top() + self.icon_rect.height() * 0.2)),  # right bottom
            QPoint(int(icon_x - len_of_side), int(self.icon_rect.top() + self.icon_rect.height() * 0.2 + len_of_side)),
            QPoint(int(icon_x - len_of_side - len_of_handle), int(self.icon_rect.top() + self.icon_rect.height() * 0.2 + len_of_side)),
            # back top
            QPoint(int(icon_x - len_of_side - len_of_handle), int(self.icon_rect.top() + self.icon_rect.height() * 0.8 - len_of_side)),
            # back bottom
            QPoint(int(icon_x - len_of_side), int(self.icon_rect.top() + self.icon_rect.height() * 0.8 - len_of_side))
        ]))
        painter.setBrush(Qt.NoBrush)

        # if self.mute:
        #     font = QFont()
        #     font.setFamily("cursive")
        #     font.setPointSize(11)
        #     painter.setFont(font)
        #     painter.drawText(QRect(int(icon_x+5), int(self.icon_rect.top()+6), 30, 30), 0, "X")

        painter.setPen(QPen(color))
        arc1_rect = QRect(int(icon_x-12), (self.icon_rect.top() + 10),
                          20, self.icon_rect.height() - 20)
        painter.drawArc(arc1_rect, 16 * 45, 16 * -90)
        arc2_rect = QRect(int(icon_x - 17), (self.icon_rect.top() + 5),
                          30, self.icon_rect.height() - 10)
        painter.drawArc(arc2_rect, 16 * 45, 16 * -90)
        arc3_rect = QRect(int(icon_x - 22), (self.icon_rect.top()),
                          40, self.icon_rect.height())
        painter.drawArc(arc3_rect, 16 * 45, 16 * -90)

        if self.mute or self.volume == 0:
            pen = QPen(color)
            pen.setWidth(2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(arc3_rect.x() + 5, arc3_rect.y(), arc3_rect.right(), arc3_rect.bottom())

        self.volume_slider.paint(painter, color)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.icon_rect.contains(event.pos()):
            self.mute = not self.mute
            self.update_screen()
        # elif self.precise_slider_rect.contains(event.pos()):
        #     self.volume = self.calc_volume_from_pos(event.pos().x())
        #     self.mouse_down_volume = True
        #     self.screen_update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        # print('mouse release')
        if self.mouse_down_volume:
            self.mouse_down_volume = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # print('mouse move')
        if self.mouse_down_volume:
            self.volume = self.calc_volume_from_pos(event.pos().x())
            self.update_screen()

    def calc_volume_from_pos(self, x):
        volume = (x - self.precise_slider_rect.left()) / self.precise_slider_rect.width()
        return min(max(0, volume), 1)
