from enum import Enum, auto, unique

from PyQt5.QtCore import QObject, pyqtSignal, QUrl

from goddo_player.singleton_meta import singleton


@unique
class PlayCommand(Enum):
    TOGGLE = auto()
    PLAY = auto()
    PAUSE = auto()


@singleton
class StateStoreSignals(QObject):
    switch_preview_video_slot = pyqtSignal(QUrl, bool)
    preview_video_in_frame_slot = pyqtSignal(int)
    preview_video_out_frame_slot = pyqtSignal(int)
    preview_video_slider_update_slot = pyqtSignal()
    preview_window_play_cmd_slot = pyqtSignal(PlayCommand)
    update_preview_file_details_slot = pyqtSignal(float, int)
    add_file_slot = pyqtSignal(QUrl)
    save_slot = pyqtSignal(QUrl)
    load_slot = pyqtSignal(QUrl)
