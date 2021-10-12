from PyQt5.QtCore import QRect

from goddo_player.ui.slider import Slider
from goddo_player.ui.ui_component import UiComponent
from goddo_player.ui.volume_controls import VolumeControl


class VideoPreview(UiComponent):
    def __init__(self, update_screen, get_rect):
        super().__init__()
        self.get_rect = get_rect
        self.update_screen = update_screen

        self.volume_control = VolumeControl(self.update_screen, self.__get_volume_control_rect)
        self.time_bar_slider = Slider(self.update_screen, self.__get_time_bar_rect, 0)

    def __get_volume_control_rect(self):
        height = 50
        width = VolumeControl.TEXT_WIDTH + VolumeControl.SLIDER_WIDTH + VolumeControl.ICON_WIDTH
        return QRect(self.get_rect().right() - width, self.get_rect().bottom()-height, width, height)

    def __get_time_bar_rect(self):
        height = 20
        volume_rect = self.volume_control.get_rect()
        return QRect(self.get_rect().left()+1, volume_rect.top() - height, self.get_rect().width()-2, height)

