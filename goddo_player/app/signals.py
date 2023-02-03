from dataclasses import dataclass
from enum import Enum, auto, unique
import itertools
import logging
from typing import Callable

from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QRect

from goddo_player.app.app_constants import WINDOW_NAME_SOURCE, WINDOW_NAME_OUTPUT
from goddo_player.app.state_store import VideoClip
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.video_path import VideoPath
from goddo_player.utils.enums import PositionType, IncDec
from goddo_player.utils.singleton_meta import singleton


@unique
class PlayCommand(Enum):
    TOGGLE = auto()
    PLAY = auto()
    PAUSE = auto()

@dataclass(frozen=True)
class SignalFunctionId:
    id: int

    @staticmethod
    def no_function():
        return SignalFunctionId(-1)


class SignalFunctionRepo:
    def __init__(self):
        self._repo = {}
        self._id_iter = itertools.count()

    @staticmethod
    def _do_nothing_fn(p1 = None, p2 = None, p3 = None, p4 = None, p5 = None, p6 = None, p7 = None, p8 = None):
        pass

    def push(self, fn: Callable) -> SignalFunctionId:
        fn_id = next(self._id_iter)
        logging.info(f'=== push fn id - {fn_id}')
        self._repo[fn_id] = fn
        return SignalFunctionId(fn_id)

    def pop(self, fn_id: SignalFunctionId) -> Callable:
        logging.info(f'=== pop fn id - {fn_id}')
        if fn_id.id != SignalFunctionId.no_function().id:
            return self._repo.pop(fn_id.id)
        else:
            return self._do_nothing_fn

class PreviewWindowSignals(QObject):
    def __init__(self, name: str):
        super().__init__()
        self.setObjectName(name)

    switch_video_slot = pyqtSignal(VideoPath, FrameInOut, SignalFunctionId)
    switch_speed_slot = pyqtSignal()
    in_frame_slot = pyqtSignal(int)
    out_frame_slot = pyqtSignal(int)
    slider_update_slot = pyqtSignal()
    play_cmd_slot = pyqtSignal(PlayCommand)
    seek_slot = pyqtSignal(int, PositionType)
    update_file_details_slot = pyqtSignal(float, int)
    update_skip_slot = pyqtSignal(IncDec)
    update_volume = pyqtSignal(float)
    switch_restrict_frame_slot = pyqtSignal()
    reset_slot = pyqtSignal()

    def __repr__(self):
        return f"PreviewWindowSignals(objectName={self.objectName()})"


@singleton
class StateStoreSignals(QObject):
    preview_window = PreviewWindowSignals(WINDOW_NAME_SOURCE)
    preview_window_output = PreviewWindowSignals(WINDOW_NAME_OUTPUT)
    add_timeline_clip_slot = pyqtSignal(VideoClip, int)
    add_file_slot = pyqtSignal(VideoPath)
    add_video_tag_slot = pyqtSignal(VideoPath, str)
    remove_video_tag_slot = pyqtSignal(VideoPath, str)
    add_clip_slot = pyqtSignal(str,VideoClip) #clip index on timeline
    add_clip_tag_slot = pyqtSignal(VideoClip, str)
    remove_clip_tag_slot = pyqtSignal(VideoClip, str)
    save_slot = pyqtSignal(VideoPath)
    load_slot = pyqtSignal(VideoPath)
    close_file_slot = pyqtSignal()
    timeline_select_clip = pyqtSignal(int)
    timeline_delete_selected_clip_slot = pyqtSignal()
    timeline_update_width_of_one_min_slot = pyqtSignal(IncDec)
    timeline_clip_double_click_slot = pyqtSignal(int, VideoClip, SignalFunctionId)
    timeline_set_clipboard_clip_slot = pyqtSignal(VideoClip)
    timeline_clear_clipboard_clip_slot = pyqtSignal()
    activate_all_windows_slot = pyqtSignal(str)

    fn_repo = SignalFunctionRepo()

    def get_preview_window(self, window_name):
        return self.preview_window if window_name == WINDOW_NAME_SOURCE else self.preview_window_output



