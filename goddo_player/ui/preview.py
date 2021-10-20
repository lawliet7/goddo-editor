import os
import sys

from PyQt5.QtCore import QRect, QEvent, QTimer
from PyQt5.QtGui import QPainter, QDragEnterEvent, QDropEvent

from goddo_player.VideoPlayer import VideoPlayer
from goddo_player.draw_utils import numpy_to_pixmap
from goddo_player.save_state import State
from goddo_player.ui.play_button import PlayButton
from goddo_player.ui.slider import Slider
from goddo_player.ui.ui_component import UiComponent
from goddo_player.ui.volume_controls import VolumeControl


class VideoPreview(UiComponent):
    def __init__(self, screen_update_fn, get_rect):
        super().__init__(screen_update_fn, get_rect)

        self.volume_control = VolumeControl(self.screen_update, self.__get_volume_control_rect)
        self.time_bar_slider = Slider(self.screen_update, self.__get_time_bar_rect, 0)
        self.play_button = PlayButton(self.screen_update, self.__get_play_btn_rect)

        state = State(os.path.join('..', '..', 'state', 'a.json'), '')
        self.video_player = VideoPlayer(state)
        self.timer = QTimer()

        self.installEventFilter(self)
        self.is_mouse_over = False

        state.save(self)

        self.frame = None

    def __get_volume_control_rect(self):
        height = 50
        width = VolumeControl.TEXT_WIDTH + VolumeControl.SLIDER_WIDTH + VolumeControl.ICON_WIDTH
        return QRect(self.get_rect().right() - width, self.get_rect().bottom()-height, width, height)

    def __get_time_bar_rect(self):
        height = 20
        volume_rect = self.volume_control.get_rect()
        return QRect(self.get_rect().left()+1, volume_rect.top() - height, self.get_rect().width()-2, height)

    def __get_play_btn_rect(self):
        height = 50
        return QRect(self.get_rect().left()+5, self.get_rect().bottom() - height, height, height)

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        if event.type() == QEvent.Enter:
            return False
        elif event.type() == QEvent.Leave:
            return False
        elif event.type() == QEvent.DragEnter:
            return False
        elif event.type() == QEvent.Drop:
            return False

        return super().eventFilter(obj, event)

    def mouseEnterEvent(self, event: QEvent) -> None:
        self.is_mouse_over = True
        self.screen_update()

    def mouseLeaveEvent(self, event: QEvent) -> None:
        self.is_mouse_over = False
        self.screen_update()

    def paint(self, painter: QPainter):
        if self.frame is not None:
            painter.drawPixmap(self.get_rect(), numpy_to_pixmap(self.frame))

        if self.is_mouse_over:
            super().paint(painter)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        # print(f'drag enter {event.mimeData().text()}')
        filename = event.mimeData().text()
        if filename.endswith('.mp4') or filename.endswith('.wmv'):
            event.accept()

    def onDropEvent(self, event: QDropEvent) -> None:
        # print(f'file dropped: {event.mimeData().text()}')
        self.video_player.switch_source(event.mimeData().text())

        self.timer.stop()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_next_frame)
        self.timer.start(int(round(1000 / self.video_player.fps)))

    def update_next_frame(self):
        self.frame = self.video_player.get_next_frame()
        self.screen_update()



