import logging
import os
import pathlib
import shutil
from dataclasses import dataclass, field, asdict
from typing import List, ClassVar

from PyQt5.QtCore import QObject, QUrl
from tinydb import TinyDB
from tinydb.table import Table

from goddo_player.frame_in_out import FrameInOut
from goddo_player.player_configs import PlayerConfigs
from goddo_player.singleton_meta import singleton


@dataclass
class PreviewWindowState:
    video_url: QUrl = None
    fps = 0
    total_frames = 0
    frame_in_out = FrameInOut()
    current_frame_no = -1
    is_max_speed = False
    time_skip_multiplier = 6

    def as_dict(self):
        return {
            "video_url": self.video_url.path() if self.video_url is not None else None,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "frame_in_out": asdict(self.frame_in_out),
            "current_frame_no": self.current_frame_no,
            "is_max_speed": self.is_max_speed,
            "time_skip_multiplier": self.time_skip_multiplier,
        }

    @staticmethod
    def from_dict(json_dict):
        prev_wind_state = PreviewWindowState()
        prev_wind_state.video_url = QUrl.fromLocalFile(json_dict['video_url'])
        prev_wind_state.fps = json_dict['fps']
        prev_wind_state.total_frames = json_dict['total_frames']
        prev_wind_state.current_frame_no = json_dict['current_frame_no']
        prev_wind_state.is_max_speed = json_dict['is_max_speed']
        prev_wind_state.time_skip_multiplier = json_dict['time_skip_multiplier']
        return prev_wind_state


@dataclass
class FileListStateItem:
    name: QUrl

    def as_dict(self):
        return {
            "name": self.name.path()
        }

    @staticmethod
    def from_dict(json_dict):
        return FileListStateItem(name=QUrl.fromLocalFile(json_dict['name']))


@dataclass
class FileListState:
    files: List[FileListStateItem] = field(default_factory=list)

    def create_file_item(self, url: 'QUrl'):
        item = FileListStateItem(url)
        # item.name = url
        return item

    def add_file_item(self, item: FileListStateItem):
        print(f'before adding {self.files}')
        self.files.append(item)
        print(f'after adding {self.files}')


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
    width_of_one_min = PlayerConfigs.timeline_initial_width_of_one_min

    def as_dict(self):
        return {
            "clips": [x.as_dict() for x in self.clips],
            "width_of_one_min": self.width_of_one_min,
        }

    @staticmethod
    def from_dict(json_dict):
        return TimelineState(
            clips=[TimelineClip.from_dict(x) for x in json_dict['clips']],
            width_of_one_min=json_dict['width_of_one_min'])


@singleton
class StateStore(QObject):
    def __init__(self):
        super().__init__()

        self.preview_window: PreviewWindowState = PreviewWindowState()
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

        logging.info(f'preview {self.preview_window}')
        logging.info(f'files {self.file_list}')

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

        self.preview_window: PreviewWindowState = PreviewWindowState()
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
