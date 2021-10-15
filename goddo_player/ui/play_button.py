from PyQt5.QtCore import QObject, QPoint, QEvent, pyqtSignal, QRect, Qt
from PyQt5.QtGui import QMouseEvent, QColor, QBrush, QPen, QPainter, QPolygon, QKeyEvent

from goddo_player.ui.draw_utils import scale_rect, midpoint
from goddo_player.ui.ui_component import UiComponent


class PlayButton(UiComponent):
    # value_update_slot = pyqtSignal(float)

    def __init__(self, screen_update_fn, get_rect):
        super().__init__(screen_update_fn, get_rect)

        self.rect_scale_pct = 0.15
        self.is_playing = False

    def __draw_play(self, painter: QPainter):
        rect = scale_rect(self.get_rect(), self.rect_scale_pct)

        painter.drawPolygon(QPolygon([
            QPoint(rect.left(), rect.top()),
            QPoint(rect.left(), rect.bottom()),
            QPoint(rect.right(), midpoint(rect.top(), rect.bottom()))
        ]))

    def __draw_pause(self, painter: QPainter):
        rect = scale_rect(self.get_rect(), self.rect_scale_pct)

        bar_width = rect.width() * 0.4
        radius = 3
        bar1 = QRect(rect.left(), rect.top(), bar_width, rect.height())
        bar2 = QRect(rect.left() + rect.width() * 0.6, rect.top(), bar_width, rect.height())
        painter.drawRoundedRect(bar1, radius, radius)
        painter.drawRoundedRect(bar2, radius, radius)

    def paint(self, painter, color=QColor('white')):
        # print(f"paint slider {self.get_rect()}")

        painter.setPen(QPen(color))

        if self.is_playing:
            self.__draw_play(painter)
        else:
            self.__draw_pause(painter)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Space:
            self.is_playing = not self.is_playing
            self.screen_update()
        else:
            super().keyPressEvent(event)
