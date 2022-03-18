from enum import Enum, auto, unique

from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QRect

from goddo_player.app.app_constants import WINDOW_NAME_SOURCE, WINDOW_NAME_OUTPUT
from goddo_player.app.state_store import TimelineClip
from goddo_player.utils.video_path import VideoPath
from goddo_player.utils.enums import PositionType, IncDec
from goddo_player.utils.singleton_meta import singleton


@unique
class PlayCommand(Enum):
    TOGGLE = auto()
    PLAY = auto()
    PAUSE = auto()


class PreviewWindowSignals(QObject):
    def __init__(self, name: str):
        super().__init__()
        self.setObjectName(name)

    switch_video_slot = pyqtSignal(VideoPath, bool)
    switch_speed_slot = pyqtSignal()
    in_frame_slot = pyqtSignal(int)
    out_frame_slot = pyqtSignal(int)
    slider_update_slot = pyqtSignal()
    play_cmd_slot = pyqtSignal(PlayCommand)
    seek_slot = pyqtSignal(int, PositionType)
    update_file_details_slot = pyqtSignal(float, int)
    update_skip_slot = pyqtSignal(IncDec)
    reset_slot = pyqtSignal()

    def __repr__(self):
        return f"PreviewWindowSignals(objectName={self.objectName()})"


@singleton
class StateStoreSignals(QObject):
    preview_window = PreviewWindowSignals(WINDOW_NAME_SOURCE)
    preview_window_output = PreviewWindowSignals(WINDOW_NAME_OUTPUT)
    add_timeline_clip_slot = pyqtSignal(TimelineClip, int)
    add_file_slot = pyqtSignal(VideoPath)
    add_video_tag_slot = pyqtSignal(VideoPath, str)
    remove_video_tag_slot = pyqtSignal(QUrl, str)
    save_slot = pyqtSignal(VideoPath)
    load_slot = pyqtSignal(VideoPath)
    close_file_slot = pyqtSignal()
    timeline_delete_selected_clip_slot = pyqtSignal()
    timeline_update_width_of_one_min_slot = pyqtSignal(IncDec)
    timeline_clip_double_click_slot = pyqtSignal(int, TimelineClip, QRect)
    activate_all_windows_slot = pyqtSignal()

    def get_preview_window(self, window_name):
        return self.preview_window if window_name == WINDOW_NAME_SOURCE else self.preview_window_output



