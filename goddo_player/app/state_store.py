import logging
import os
import pathlib
import shutil
from dataclasses import dataclass, field, asdict, fields
from typing import List, Dict

from PyQt5.QtCore import QObject, QUrl
from tinydb import TinyDB
from tinydb.table import Table

from goddo_player.app.app_constants import WINDOW_NAME_SOURCE, WINDOW_NAME_OUTPUT
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.utils.mru_priority_set import MRUPrioritySet
from goddo_player.utils.time_frame_utils import build_time_str, frames_to_time_components
from goddo_player.utils.video_path import VideoPath
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.singleton_meta import singleton
from goddo_player.utils.url_utils import file_to_url


@dataclass
class PreviewWindowState:
    name: str
    video_path: VideoPath = field(default=VideoPath(QUrl()))
    fps: float = field(default=0)
    total_frames: int = field(default=0)
    frame_in_out: FrameInOut = field(default_factory=FrameInOut)
    current_frame_no: int = field(default=0)
    is_max_speed: bool = field(default=False)
    time_skip_multiplier: int = field(default=1)
    cur_total_frames: int = field(default=0)
    # start/end frame on output window, in_frame - extra left frames, out_frame + extra right frames
    cur_start_frame: int = field(default=0)
    cur_end_frame: int = field(default=0)
    restrict_frame_interval: bool = field(default=False)
    volume: float = field(default=PlayerConfigs.default_volume)

    def __post_init__(self):
        self.restrict_frame_interval = True if self.name == WINDOW_NAME_OUTPUT else False

    def as_dict(self):
        return {
            "video_path": self.video_path.str() if self.video_path is not None else None,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "frame_in_out": asdict(self.frame_in_out),
            "current_frame_no": self.current_frame_no,
            "is_max_speed": self.is_max_speed,
            "time_skip_multiplier": self.time_skip_multiplier,
            "cur_total_frames": self.cur_total_frames,
            "cur_start_frame": self.cur_start_frame,
            "cur_end_frame": self.cur_end_frame,
            "restrict_frame_interval": self.restrict_frame_interval,
            "volume": self.volume,
        }

    @staticmethod
    def from_dict(json_dict):
        prev_wind_state = PreviewWindowState(json_dict['name'])
        prev_wind_state.video_path = file_to_url(json_dict['video_path'])
        prev_wind_state.fps = json_dict['fps']
        prev_wind_state.total_frames = json_dict['total_frames']
        frame_in_out_dict = json_dict['frame_in_out']
        prev_wind_state.frame_in_out = FrameInOut(frame_in_out_dict['in_frame'], frame_in_out_dict['out_frame'])
        prev_wind_state.current_frame_no = json_dict['current_frame_no']
        prev_wind_state.is_max_speed = json_dict['is_max_speed']
        prev_wind_state.time_skip_multiplier = json_dict['time_skip_multiplier']
        prev_wind_state.cur_total_frames = json_dict['cur_total_frames']
        prev_wind_state.cur_start_frame = json_dict['cur_start_frame']
        prev_wind_state.cur_end_frame = json_dict['cur_end_frame']
        prev_wind_state.restrict_frame_interval = json_dict['restrict_frame_interval']
        prev_wind_state.volume = json_dict['volume']
        return prev_wind_state


@dataclass
class AppConfig:
    extra_frames_in_secs_config: int = field(default=PlayerConfigs.default_extra_frames_in_secs)

    def as_dict(self):
        return asdict(self)


@dataclass
class FileListStateItem:
    name: VideoPath
    tags: List[str] = field(default_factory=list)

    def as_dict(self):
        return {
            "name": self.name.str(),
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(json_dict):
        return FileListStateItem(name=file_to_url(json_dict['name'], json_dict['tags']))

    def add_tag(self, tag: str):
        new_tags = self.tags[:]
        new_tags.append(tag)
        self.tags = new_tags

    def delete_tag(self, tag: str):
        if tag in self.tags:
            idx = self.tags.index(tag)
            self.tags = [tag for i, tag in enumerate(self.tags) if i != idx]
            return idx
        else:
            return -1


@dataclass
class ClipListStateItem:
    name: QUrl
    frame_in_out: FrameInOut
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.frame_in_out.in_frame is None or self.frame_in_out.out_frame is None:
            raise Exception(f'For clip item, the frame in/out cannot be blank. frame_in_out={self.frame_in_out}')

    def as_dict(self):
        return {
            "name": self.name.path(),
            "frame_in_out": asdict(self.frame_in_out),
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(json_dict):
        frame_in_out_dict = json_dict['frame_in_out']
        frame_in_out = FrameInOut(frame_in_out_dict['in_frame'], frame_in_out_dict['out_frame'])
        return ClipListStateItem(name=QUrl.fromLocalFile(json_dict['name']),
                                 frame_in_out=frame_in_out, tags=json_dict['tags'])

    def add_tag(self, tag: str):
        new_tags = self.tags[:]
        new_tags.append(tag)
        self.tags = new_tags

    def delete_tag(self, tag: str):
        if tag in self.tags:
            idx = self.tags.index(tag)
            self.tags = [tag for i, tag in enumerate(self.tags) if i != idx]
            return idx
        else:
            return -1


@dataclass
class ClipListState:
    clips: List[ClipListStateItem] = field(default_factory=list)
    clips_dict: Dict[str, ClipListStateItem] = field(default_factory=dict)

    def as_dict(self):
        return {
            "clips": [c.as_dict() for c in self.clips],
            "clips_dict": {k:v.as_dict() for (k,v) in self.clips_dict.items()}
        }

    @staticmethod
    def create_file_item(url: QUrl, frame_in_out: FrameInOut):
        return ClipListStateItem(url, frame_in_out)

    def add_file_item(self, item: ClipListStateItem):
        logging.debug(f'before adding {self.files}')
        self.files.append(item)
        self.files_dict[item.name.path()] = item
        logging.debug(f'after adding {self.files}')


@dataclass
class FileListState:
    files: List[FileListStateItem] = field(default_factory=list)
    files_dict: Dict[str, FileListStateItem] = field(default_factory=dict)

    def as_dict(self):
        return {
            "files": [f.as_dict() for f in self.files],
            "files_dict": {k:v.as_dict() for (k,v) in self.files_dict.items()}
        }

    @staticmethod
    def create_file_item(video_path: VideoPath):
        item = FileListStateItem(video_path)
        # item.name = url
        return item

    def add_file_item(self, item: FileListStateItem):
        logging.debug(f'before adding {self.files}')
        self.files.append(item)
        self.files_dict[item.name.str()] = item
        logging.debug(f'after adding {self.files}')


@dataclass(frozen=True)
class VideoClip:
    video_path: VideoPath
    fps: float
    total_frames: int
    frame_in_out: FrameInOut

    def as_dict(self):
        return {
            "video_path": self.video_path.str(),
            "fps": self.fps,
            "total_frames": self.total_frames,
            "frame_in_out": asdict(self.frame_in_out),
        }

    @staticmethod
    def from_dict(json_dict):
        return VideoClip(VideoPath(file_to_url(json_dict['video_path'])), json_dict['fps'],
                            json_dict['total_frames'], FrameInOut(**json_dict['frame_in_out']))

    def get_total_time_str(self, overridden_total_frames=None):
        final_total_frames = overridden_total_frames if overridden_total_frames else self.total_frames
        return build_time_str(*frames_to_time_components(final_total_frames, self.fps))

@dataclass
class TimelineState:
    clips: List[VideoClip] = field(default_factory=list)
    width_of_one_min: int = field(default=PlayerConfigs.timeline_initial_width_of_one_min)
    selected_clip_index: int = field(default=-1)
    opened_clip_index: int = field(default=-1)
    clipboard_clip: VideoClip = field(default=None)

    def as_dict(self):
        return {
            "clips": [x.as_dict() for x in self.clips],
            "width_of_one_min": self.width_of_one_min,
            "selected_clip_index": self.selected_clip_index,
            "opened_clip_index": self.opened_clip_index,
            "clipboard_clip": self.clipboard_clip.as_dict() if self.clipboard_clip else None,
        }

    @staticmethod
    def from_dict(json_dict):
        return TimelineState(
            clips=[VideoClip.from_dict(x) for x in json_dict['clips']],
            width_of_one_min=json_dict['width_of_one_min'],
            selected_clip_index=json_dict['selected_clip_index'],
            opened_clip_index=json_dict['opened_clip_index'],
            clipboard_clip=VideoClip.from_dict(json_dict['clipboard_clip']),
            )

@singleton
class StateStore(QObject):
    def __init__(self):
        super().__init__()

        self.preview_window: PreviewWindowState = PreviewWindowState(WINDOW_NAME_SOURCE)
        self.preview_window_output: PreviewWindowState = PreviewWindowState(WINDOW_NAME_OUTPUT)
        self.app_config: AppConfig = AppConfig()
        self.file_list = FileListState()
        self.clip_list = ClipListState()
        self.video_tag_cache = MRUPrioritySet(PlayerConfigs.max_tags_in_dropdown)
        self.timeline = TimelineState()
        self.cur_save_file = VideoPath(file_to_url(PlayerConfigs.default_save_file))

        self.empty_state_loader = self.EmptyStateLoader()

        logging.info(f'cur save file: {self.cur_save_file}')

    class EmptyStateLoader:
        def __init__(self):
            self.blank_pw_state: PreviewWindowState = PreviewWindowState(WINDOW_NAME_SOURCE)
            self.blank_pw_output_state: PreviewWindowState = PreviewWindowState(WINDOW_NAME_OUTPUT)
            self.blank_app_config: AppConfig = AppConfig()
            self.blank_file_list = FileListState()
            self.blank_clip_list = ClipListState()
            self.blank_timeline = TimelineState()

        def _copy_fields_from_blank(self, state_obj, blank_obj):
            for dc_field in fields(state_obj):
                field_name = dc_field.name
                value = getattr(blank_obj,field_name)
                if isinstance(value, list):
                    setattr(state_obj,field_name,value[:])
                elif isinstance(value, dict):
                    setattr(state_obj,field_name,value.copy())
                else:
                    setattr(state_obj,field_name,value)

        def reset_state(self, state_store):
            self._copy_fields_from_blank(state_store.preview_window, self.blank_pw_state)
            self._copy_fields_from_blank(state_store.preview_window_output, self.blank_pw_output_state)
            self._copy_fields_from_blank(state_store.app_config, self.blank_app_config)
            self._copy_fields_from_blank(state_store.file_list, self.blank_file_list)
            self._copy_fields_from_blank(state_store.clip_list, self.blank_clip_list)
            self._copy_fields_from_blank(state_store.timeline, self.blank_timeline)

    def as_dict(self):
        d = {}
        d['preview_window'] = self.preview_window.as_dict()
        d['preview_window_output'] = self.preview_window_output.as_dict()
        d['app_config'] = self.app_config.as_dict()
        d['file_list'] = self.file_list.as_dict()
        d['clip_list'] = self.clip_list.as_dict()
        d['timeline'] = self.timeline.as_dict()
        d['cur_save_file'] = str(self.cur_save_file)
        return d

    def save_file(self, video_path: VideoPath):

        logging.info(f'saving {video_path}')
        # todo msg box to select save file

        save_file_name = video_path.str()
        tmp_save_file_name = save_file_name + "_tmp"
        is_existing_file = pathlib.Path(save_file_name).resolve().exists()
        if is_existing_file:
            shutil.copy(save_file_name, tmp_save_file_name)

        logging.debug(f'preview {self.preview_window}')
        logging.debug(f'files {self.file_list}')

        with TinyDB(save_file_name) as db:
            table_preview_windows: Table = db.table('preview_windows')
            table_preview_window_outputs: Table = db.table('preview_window_outputs')
            table_files: Table = db.table('files')
            table_timelines: Table = db.table('timelines')

            table_files.truncate()
            for _, file in enumerate(self.file_list.files):
                table_files.insert(file.as_dict())

            table_preview_windows.truncate()
            table_preview_windows.insert(self.preview_window.as_dict())

            table_preview_window_outputs.truncate()
            table_preview_window_outputs.insert(self.preview_window_output.as_dict())

            table_timelines.truncate()
            table_timelines.insert(self.timeline.as_dict())

        # db.close()

        if is_existing_file:
            os.remove(tmp_save_file_name)

    def _get_first_row(self, table: Table):
        all = table.all()
        if len(all) > 0:
            return all.pop()

    def load_file(self, video_path: VideoPath, handle_file_fn, handle_prev_wind_fn, handle_prev_wind_output_fn, handle_timeline_fn):
        logging.info(f'loading {video_path}')
        # todo msg box to select save file

        self.empty_state_loader.reset_state(self)

        if not video_path.is_empty():
            load_file_name = video_path.str()

            db = TinyDB(load_file_name)
            table_preview_windows: Table = db.table('preview_windows')
            table_preview_window_outputs: Table = db.table('preview_window_outputs')
            table_files: Table = db.table('files')
            table_timelines: Table = db.table('timelines')

            all_files = table_files.all()
            for file_dict in all_files:
                handle_file_fn(file_dict)

            for prev_wind_dict in table_preview_windows.all():
                if prev_wind_dict['video_path']:
                    timeline_dict = self._get_first_row(table_timelines)
                    prev_wind_outputs_dict = self._get_first_row(table_preview_window_outputs)

                    handle_prev_wind_fn(prev_wind_dict, timeline_dict, prev_wind_outputs_dict)

            db.close()

            self.cur_save_file = video_path

            logging.info(f'finished loading {video_path}')
            logging.info(f'preview {self.preview_window}')
            logging.info(f'files {self.file_list}')

        self.cur_save_file = video_path

    def get_preview_window(self, window_name):
        return self.preview_window if window_name == self.preview_window.name else self.preview_window_output
