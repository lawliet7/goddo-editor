from enum import Enum, auto, unique

from PyQt5.QtCore import QObject, pyqtSignal, QUrl

from goddo_player.enums import PositionType
from goddo_player.singleton_meta import singleton
from goddo_player.state_store import TimelineClip


@unique
class PlayCommand(Enum):
    TOGGLE = auto()
    PLAY = auto()
    PAUSE = auto()


@singleton
class PreviewWindowSignals(QObject):
    switch_video_slot = pyqtSignal(QUrl, bool)
    switch_speed_slot = pyqtSignal()
    in_frame_slot = pyqtSignal(int)
    out_frame_slot = pyqtSignal(int)
    slider_update_slot = pyqtSignal()
    play_cmd_slot = pyqtSignal(PlayCommand)
    seek_slot = pyqtSignal(int, PositionType)
    update_file_details_slot = pyqtSignal(float, int)


@singleton
class StateStoreSignals(QObject):
    preview_window = PreviewWindowSignals()
    add_timeline_clip_slot = pyqtSignal(TimelineClip)
    add_file_slot = pyqtSignal(QUrl)
    save_slot = pyqtSignal(QUrl)
    load_slot = pyqtSignal(QUrl)
    timeline_delete_selected_clip_slot = pyqtSignal()



