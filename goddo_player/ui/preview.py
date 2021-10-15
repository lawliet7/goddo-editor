from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QKeyEvent

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

