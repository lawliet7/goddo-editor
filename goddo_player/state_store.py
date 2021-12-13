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
from goddo_player.singleton_meta import singleton


@dataclass
class PreviewWindowState:
    video_url: QUrl = None
    fps = 0
    total_frames = 0
    frame_in_out = FrameInOut()
    current_frame_no = -1
    is_max_speed = False

    def as_dict(self):
        return {
            "video_url": self.video_url.path() if self.video_url is not None else None,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "frame_in_out": asdict(self.frame_in_out),
            "current_frame_no": self.current_frame_no,
            "is_max_speed": self.is_max_speed,
        }

    @staticmethod
    def from_dict(json_dict):
        prev_wind_state = PreviewWindowState()
        prev_wind_state.video_url = QUrl.fromLocalFile(json_dict['video_url'])
        prev_wind_state.fps = json_dict['fps']
        prev_wind_state.total_frames = json_dict['total_frames']
        prev_wind_state.current_frame_no = json_dict['current_frame_no']
        prev_wind_state.is_max_speed = json_dict['is_max_speed']
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
    # def __init__(self):
    #     super().__init__()
    #     self.files: List[FileListStateItem] = []
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

    def as_dict(self):
        return {
            "clips": [x.as_dict() for x in self.clips]
        }

    @staticmethod
    def from_dict(json_dict):
        return TimelineState([TimelineClip.from_dict(x) for x in json_dict['clips']])


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


# from dataclasses import asdict
#
# import cv2
# from PyQt5.QtCore import QObject, pyqtSignal, QUrl, pyqtSlot
# from tinydb import TinyDB
# from tinydb.table import Table
#
# from goddo_player.frame_in_out import FrameInOut
# from goddo_player.singleton_meta import singleton
#
#
# @singleton
# class State(QObject):
#     update_preview_file_slot = pyqtSignal(str, QUrl)
#     new_preview_slot = pyqtSignal(str)
#     new_file_slot = pyqtSignal(str)
#     new_file_added_slot = pyqtSignal(str)
#     load_slot = pyqtSignal(str)
#     save_slot = pyqtSignal()
#     play_slot = pyqtSignal(str)
#     pause_slot = pyqtSignal(str)
#     post_pause_slot = pyqtSignal(str, int)
#     jump_frame_slot = pyqtSignal(str, int)
#     preview_in_frame_slot = pyqtSignal(str, int)
#     preview_out_frame_slot = pyqtSignal(str, int)
#     add_timeline_clip_slot = pyqtSignal(dict)
#     change_speed_slot = pyqtSignal(str, int)
#
#     def __init__(self):
#         super().__init__()
#         # print(f'save file {save_file}')
#         # is_existing_file = pathlib.Path(self.save_file).resolve().exists()
#
#         self.save_file = None
#         self.db = None
#         self.table_preview_windows: Table = None
#         self.table_files: Table = None
#         self.table_timelines: Table = None
#         # video_table = self.db.table('videos')
#
#         self.preview_windows = {}
#         self.files = []
#         self.timeline = {
#             "clips": []
#         }
#
#         self.update_preview_file_slot.connect(self.__on_update_preview_file)
#         self.new_preview_slot.connect(self.__on_new_preview)
#         self.new_file_slot.connect(self.__on_new_file)
#         self.load_slot.connect(self.__load_file)
#         self.save_slot.connect(self.__save_file)
#         self.post_pause_slot.connect(self.__post_pause_handler)
#         self.preview_in_frame_slot.connect(self.__preview_in_frame_handler)
#         self.preview_out_frame_slot.connect(self.__preview_out_frame_handler)
#         self.add_timeline_clip_slot.connect(self.__add_timeline_clip_handler)
#         self.change_speed_slot.connect(self.__change_speed_handler)
#
#     def __add_timeline_clip_handler(self, clip):
#         self.timeline = {
#             **self.timeline,
#             'clips': self.timeline['clips'] + [clip],
#         }
#         print(self.timeline)
#
#     def __preview_in_frame_handler(self, name: str, frame_no: int):
#         new_dict1 = {
#             **self.preview_windows[name],
#             'frame_in_out': self.preview_windows[name]['frame_in_out'].update_in_frame(frame_no),
#         }
#
#         new_dict = {
#             **self.preview_windows,
#             name: new_dict1,
#         }
#         self.preview_windows = new_dict
#         print(self.preview_windows)
#
#     def __preview_out_frame_handler(self, name: str, frame_no: int):
#         new_dict1 = {
#             **self.preview_windows[name],
#             'frame_in_out': self.preview_windows[name]['frame_in_out'].update_out_frame(frame_no),
#         }
#
#         new_dict = {
#             **self.preview_windows,
#             name: new_dict1,
#         }
#         self.preview_windows = new_dict
#         print(self.preview_windows)
#
#     def __post_pause_handler(self, name: str, frame_no: int):
#         new_dict1 = {
#             **self.preview_windows[name],
#             'frame_no': frame_no,
#         }
#
#         new_dict = {
#             **self.preview_windows,
#             name: new_dict1,
#         }
#         self.preview_windows = new_dict
#         print(self.preview_windows)
#
#     def __load_file(self, save_file):
#         self.db = TinyDB(save_file)
#         self.table_preview_windows: Table = self.db.table('preview_windows')
#         self.table_files: Table = self.db.table('files')
#         self.table_timelines: Table = self.db.table('timelines')
#         self.save_file = save_file
#
#         self.preview_windows = {}
#         self.files = []
#
#         all_files = self.table_files.all()
#         for file in all_files:
#             self.new_file_slot.emit(file["file_path"])
#
#         all_preview_windows = self.table_preview_windows.all()
#         for preview_window in all_preview_windows:
#             self.new_preview_slot.emit(preview_window['name'])
#             if preview_window['video_file']:
#                 self.update_preview_file_slot.emit(preview_window['name'], QUrl(preview_window['video_file']))
#                 if preview_window['frame_in_out']['in_frame']:
#                     self.preview_in_frame_slot.emit('source', preview_window['frame_in_out']['in_frame'])
#                 if preview_window['frame_in_out']['out_frame']:
#                     self.preview_out_frame_slot.emit('source', preview_window['frame_in_out']['out_frame'])
#                 self.jump_frame_slot.emit(preview_window['name'], preview_window['frame_no'])
#
#         if 'source' not in self.preview_windows:
#             self.new_preview_slot.emit('source')
#
#         all_timelines = self.table_timelines.all()
#         for timeline in all_timelines:
#             for clip in timeline['clips']:
#                 db_frame_in_out = clip['frame_in_out']
#                 self.add_timeline_clip_slot.emit({
#                     "source": QUrl(clip['source']),
#                     "frame_in_out": FrameInOut(db_frame_in_out['in_frame'], db_frame_in_out['out_frame']),
#                 })
#
#     @pyqtSlot(str, QUrl)
#     def __on_update_preview_file(self, name, file):
#         cap = cv2.VideoCapture(file.path())
#         fps = cap.get(cv2.CAP_PROP_FPS)
#         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#         cap.release()
#
#         new_dict1 = {
#             **self.preview_windows[name],
#             'video_file': file,
#             'video_details': {
#                 'fps': fps,
#                 'total_frames': total_frames,
#             },
#             'frame_no': 0,
#             'frame_in_out': FrameInOut(),
#             'speed': 0,  # >1, 1, -1, -2, ...
#         }
#
#         new_dict = {
#             **self.preview_windows,
#             name: new_dict1,
#         }
#         self.preview_windows = new_dict
#         print(self.preview_windows)
#
#         self.change_speed_slot.emit('source', int(1000 / fps) + 1)
#
#     def __change_speed_handler(self, name, speed):
#         new_dict1 = {
#             **self.preview_windows[name],
#             'speed': speed,
#         }
#
#         new_dict = {
#             **self.preview_windows,
#             name: new_dict1,
#         }
#         self.preview_windows = new_dict
#         print(self.preview_windows)
#
#     @pyqtSlot(str)
#     def __on_new_preview(self, name):
#         if name not in self.preview_windows.keys():
#             print(f'new preview window {name}')
#             new_dict1 = {
#                 'video_file': None,
#                 'frame_no': 0,
#                 'frame_in_out': FrameInOut()
#             }
#
#             new_dict = {
#                 **self.preview_windows,
#                 name: new_dict1,
#             }
#             self.preview_windows = new_dict
#             print(self.preview_windows)
#         else:
#             raise Exception(f"duplicate preview window {name}")
#
#     @pyqtSlot(str)
#     def __on_new_file(self, file):
#         print('on new file')
#
#         if len([x for x in self.files if x['file_path'] == file]) == 0:
#             print(f'not duplicate {file}')
#             cap = cv2.VideoCapture(file)
#             data = {
#                 'file_path': file,
#                 'fps': cap.get(cv2.CAP_PROP_FPS),
#                 'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
#             }
#             cap.release()
#             self.files = self.files + [data]
#             self.new_file_added_slot.emit(file)
#
#     @pyqtSlot()
#     def __save_file(self):
#
#         print('save it')
#         # todo msg box to select save file
#
#         self.table_files.truncate()
#
#         for i, file in enumerate(self.files):
#             self.table_files.insert({
#                 'file_path': file['file_path'],
#                 'order': i+1,
#             })
#
#         self.table_preview_windows.truncate()
#         self.table_preview_windows.insert({
#             'name': 'source',
#             'video_file': self.__file_path_to_url(self.preview_windows['source']['video_file']),
#             'frame_no': self.preview_windows['source']['frame_no'],
#             'frame_in_out': asdict(self.preview_windows['source']['frame_in_out']),
#         })
#
#         self.table_timelines.truncate()
#         self.table_timelines.insert({
#             'name': 'default',
#             'clips': [self.__timeline_clip_to_db_dict(clip) for clip in self.timeline['clips']],
#         })
#
#     def __timeline_clip_to_db_dict(self, timeline_clip: dict):
#         return {
#             "source": timeline_clip['source'].path(),
#             "frame_in_out": asdict(timeline_clip['frame_in_out'])
#         }
#
#     def __file_path_to_url(self, url_file_path: QUrl) -> str:
#         if url_file_path:
#             return url_file_path.url()
#         else:
#             return None
