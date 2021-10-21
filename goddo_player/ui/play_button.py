from PyQt5.QtCore import QObject, QPoint, QEvent, pyqtSignal, QRect, Qt, pyqtSlot
from PyQt5.QtGui import QMouseEvent, QColor, QBrush, QPen, QPainter, QPolygon, QKeyEvent

from goddo_player.ui.draw_utils import scale_rect, midpoint
from goddo_player.ui.ui_component import UiComponent


class PlayButton(UiComponent):
    play_slot = pyqtSignal()
    pause_slot = pyqtSignal()

    def __init__(self, parent, get_rect):
        super().__init__(parent, get_rect)

        self.rect_scale_pct = 0.15
        # self.is_playing = False

        self.play_slot.connect(self.play_handler)
        self.pause_slot.connect(self.pause_handler)
        self.draw_function = self.__draw_play

    @property
    def is_playing(self):
        return self.draw_function == self.__draw_pause

    @pyqtSlot()
    def play_handler(self):
        self.draw_function = self.__draw_pause
        self.window.update()

    @pyqtSlot()
    def pause_handler(self):
        self.draw_function = self.__draw_play
        self.window.update()

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
        painter.setPen(QPen(color))
        self.draw_function(painter)

