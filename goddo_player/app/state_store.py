import logging
import os
import pathlib
import shutil
from dataclasses import dataclass, field, asdict
from typing import List

from PyQt5.QtCore import QObject, QUrl
from tinydb import TinyDB
from tinydb.table import Table

from goddo_player.frame_in_out import FrameInOut
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.app_constants import WINDOW_NAME_SOURCE, WINDOW_NAME_OUTPUT
from goddo_player.utils.singleton_meta import singleton


@dataclass
class PreviewWindowState:
    name: str
    video_url: QUrl = None
    fps: float = field(default=0)
    total_frames: int = field(default=0)
    frame_in_out: FrameInOut = field(default_factory=FrameInOut)
    current_frame_no: int = field(default=-1)
    is_max_speed: bool = field(default=False)
    time_skip_multiplier: int = field(default=1)
    cur_total_frames: int = field(default=0)
    cur_start_frame: int = field(default=0)
    cur_end_frame: int = field(default=0)

    def as_dict(self):
        return {
            "video_url": self.video_url.path() if self.video_url is not None else None,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "frame_in_out": asdict(self.frame_in_out),
            "current_frame_no": self.current_frame_no,
            "is_max_speed": self.is_max_speed,
            "time_skip_multiplier": self.time_skip_multiplier,
            "cur_total_frames": self.cur_total_frames,
            "cur_start_frame": self.cur_start_frame,
            "cur_end_frame": self.cur_end_frame,
        }

    @staticmethod
    def from_dict(json_dict):
        prev_wind_state = PreviewWindowState(json_dict['name'])
        prev_wind_state.video_url = QUrl.fromLocalFile(json_dict['video_url'])
        prev_wind_state.fps = json_dict['fps']
        prev_wind_state.total_frames = json_dict['total_frames']
        prev_wind_state.current_frame_no = json_dict['current_frame_no']
        prev_wind_state.is_max_speed = json_dict['is_max_speed']
        prev_wind_state.time_skip_multiplier = json_dict['time_skip_multiplier']
        prev_wind_state.cur_total_frames = json_dict['cur_total_frames']
        prev_wind_state.cur_start_frame = json_dict['cur_start_frame']
        prev_wind_state.cur_end_frame = json_dict['cur_end_frame']
        return prev_wind_state


@dataclass
class AppConfig:
    extra_frames_in_secs_config: int = field(default=PlayerConfigs.default_extra_frames_in_secs)


@dataclass
class FileListStateItem:
    name: QUrl
    tags: List[str] = field(default_factory=lambda: [])

    def as_dict(self):
        return {
            "name": self.name.path(),
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(json_dict):
        return FileListStateItem(name=QUrl.fromLocalFile(json_dict['name'], json_dict['tags']))


@dataclass
class FileListState:
    files: List[FileListStateItem] = field(default_factory=list)

    @staticmethod
    def create_file_item(url: 'QUrl'):
        item = FileListStateItem(url)
        # item.name = url
        return item

    def add_file_item(self, item: FileListStateItem):
        logging.debug(f'before adding {self.files}')
        self.files.append(item)
        logging.debug(f'after adding {self.files}')


@dataclass(frozen=True)
class TimelineClip:
    video_url: QUrl
    fps: float
    total_frames: int
    frame_in_out: FrameInOut()

    def as_dict(self):
        return {
            "video_url": self.video_url.path(),
            "fps": self.fps,
            "total_frames": self.total_frames,
            "frame_in_out": asdict(self.frame_in_out)
        }

    @staticmethod
    def from_dict(json_dict):
        return TimelineClip(QUrl.fromLocalFile(json_dict['video_url']), json_dict['fps'],
                            json_dict['total_frames'], FrameInOut(**json_dict['frame_in_out']))


@dataclass
class TimelineState:
    clips: List[TimelineClip] = field(default_factory=list)
    width_of_one_min: int = field(default=PlayerConfigs.timeline_initial_width_of_one_min)
    selected_clip_index: int = field(default=-1)
    opened_clip_index: int = field(default=-1)
    clipboard_clip: TimelineClip = field(default=None)

    def as_dict(self):
        return {
            "clips": [x.as_dict() for x in self.clips],
            "width_of_one_min": self.width_of_one_min,
            "selected_clip_index": self.selected_clip_index,
            "opened_clip_index": self.opened_clip_index,
        }

    @staticmethod
    def from_dict(json_dict):
        return TimelineState(
            clips=[TimelineClip.from_dict(x) for x in json_dict['clips']],
            width_of_one_min=json_dict['width_of_one_min'],
            selected_clip_index=json_dict['selected_clip_index'],
            opened_clip_index=json_dict['opened_clip_index'],
            )


@singleton
class StateStore(QObject):
    def __init__(self):
        super().__init__()

        self.preview_window: PreviewWindowState = PreviewWindowState(WINDOW_NAME_SOURCE)
        self.preview_window_output: PreviewWindowState = PreviewWindowState(WINDOW_NAME_OUTPUT)
        self.app_config: AppConfig = AppConfig()
        self.file_list = FileListState()
        self.timeline = TimelineState()

    def save_file(self, url: QUrl):

        logging.info(f'saving {url}')
        # todo msg box to select save file

        save_file_name = url.path()[1:]
        tmp_save_file_name = save_file_name + "_tmp"
        is_existing_file = pathlib.Path(save_file_name).resolve().exists()
        if is_existing_file:
            shutil.copy(save_file_name, tmp_save_file_name)

        logging.debug(f'preview {self.preview_window}')
        logging.debug(f'files {self.file_list}')

        with TinyDB(save_file_name) as db:
            table_preview_windows: Table = db.table('preview_windows')
            table_files: Table = db.table('files')
            table_timelines: Table = db.table('timelines')

            table_files.truncate()
            for i, file in enumerate(self.file_list.files):
                table_files.insert(file.as_dict())

            table_preview_windows.truncate()
            table_preview_windows.insert(self.preview_window.as_dict())

            table_timelines.truncate()
            table_timelines.insert(self.timeline.as_dict())

        # db.close()

        if is_existing_file:
            os.remove(tmp_save_file_name)

    def load_file(self, url: QUrl, handle_file_fn, handle_prev_wind_fn, handle_timeline_fn):

        logging.info(f'loading {url}')
        # todo msg box to select save file

        self.preview_window: PreviewWindowState = PreviewWindowState(WINDOW_NAME_SOURCE)
        self.preview_window_output: PreviewWindowState = PreviewWindowState(WINDOW_NAME_OUTPUT)
        self.app_config: AppConfig = AppConfig()
        self.file_list = FileListState()
        self.timeline = TimelineState()

        load_file_name = url.path()[1:]

        db = TinyDB(load_file_name)
        table_preview_windows: Table = db.table('preview_windows')
        table_files: Table = db.table('files')
        table_timelines: Table = db.table('timelines')

        all_files = table_files.all()
        for file_dict in all_files:
            handle_file_fn(file_dict)

        for prev_wind_dict in table_preview_windows.all():
            if prev_wind_dict['video_url']:
                handle_prev_wind_fn(prev_wind_dict)

        for timeline_dict in table_timelines:
            handle_timeline_fn(timeline_dict)

        db.close()

        logging.info(f'finished loading {url.path()}')
        logging.info(f'preview {self.preview_window}')
        logging.info(f'files {self.file_list}')

    def get_preview_window(self, window_name):
        return self.preview_window if window_name == self.preview_window.name else self.preview_window_output
