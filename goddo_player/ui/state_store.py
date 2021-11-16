from dataclasses import asdict

import cv2
from PyQt5.QtCore import QObject, pyqtSignal, QUrl, pyqtSlot
from tinydb import TinyDB
from tinydb.table import Table

from goddo_player.ui.frame_in_out import FrameInOut
from goddo_player.ui.singleton_meta import singleton


@singleton
class State(QObject):
    update_preview_file_slot = pyqtSignal(str, QUrl)
    new_preview_slot = pyqtSignal(str)
    new_file_slot = pyqtSignal(str)
    new_file_added_slot = pyqtSignal(str)
    load_slot = pyqtSignal(str)
    save_slot = pyqtSignal()
    play_slot = pyqtSignal(str)
    pause_slot = pyqtSignal(str)
    post_pause_slot = pyqtSignal(str, int)
    jump_frame_slot = pyqtSignal(str, int)
    preview_in_frame_slot = pyqtSignal(str, int)
    preview_out_frame_slot = pyqtSignal(str, int)
    add_timeline_clip_slot = pyqtSignal(dict)
    change_speed_slot = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        # print(f'save file {save_file}')
        # is_existing_file = pathlib.Path(self.save_file).resolve().exists()

        self.save_file = None
        self.db = None
        self.table_preview_windows: Table = None
        self.table_files: Table = None
        self.table_timelines: Table = None
        # video_table = self.db.table('videos')

        self.preview_windows = {}
        self.files = []
        self.timeline = {
            "clips": []
        }

        self.update_preview_file_slot.connect(self.__on_update_preview_file)
        self.new_preview_slot.connect(self.__on_new_preview)
        self.new_file_slot.connect(self.__on_new_file)
        self.load_slot.connect(self.__load_file)
        self.save_slot.connect(self.__save_file)
        self.post_pause_slot.connect(self.__post_pause_handler)
        self.preview_in_frame_slot.connect(self.__preview_in_frame_handler)
        self.preview_out_frame_slot.connect(self.__preview_out_frame_handler)
        self.add_timeline_clip_slot.connect(self.__add_timeline_clip_handler)
        self.change_speed_slot.connect(self.__change_speed_handler)

    def __add_timeline_clip_handler(self, clip):
        self.timeline = {
            **self.timeline,
            'clips': self.timeline['clips'] + [clip],
        }
        print(self.timeline)

    def __preview_in_frame_handler(self, name: str, frame_no: int):
        new_dict1 = {
            **self.preview_windows[name],
            'frame_in_out': self.preview_windows[name]['frame_in_out'].update_in_frame(frame_no),
        }

        new_dict = {
            **self.preview_windows,
            name: new_dict1,
        }
        self.preview_windows = new_dict
        print(self.preview_windows)

    def __preview_out_frame_handler(self, name: str, frame_no: int):
        new_dict1 = {
            **self.preview_windows[name],
            'frame_in_out': self.preview_windows[name]['frame_in_out'].update_out_frame(frame_no),
        }

        new_dict = {
            **self.preview_windows,
            name: new_dict1,
        }
        self.preview_windows = new_dict
        print(self.preview_windows)

    def __post_pause_handler(self, name: str, frame_no: int):
        new_dict1 = {
            **self.preview_windows[name],
            'frame_no': frame_no,
        }

        new_dict = {
            **self.preview_windows,
            name: new_dict1,
        }
        self.preview_windows = new_dict
        print(self.preview_windows)

    def __load_file(self, save_file):
        self.db = TinyDB(save_file)
        self.table_preview_windows: Table = self.db.table('preview_windows')
        self.table_files: Table = self.db.table('files')
        self.table_timelines: Table = self.db.table('timelines')
        self.save_file = save_file

        self.preview_windows = {}
        self.files = []

        all_files = self.table_files.all()
        for file in all_files:
            self.new_file_slot.emit(file["file_path"])

        all_preview_windows = self.table_preview_windows.all()
        for preview_window in all_preview_windows:
            self.new_preview_slot.emit(preview_window['name'])
            if preview_window['video_file']:
                self.update_preview_file_slot.emit(preview_window['name'], QUrl(preview_window['video_file']))
                if preview_window['frame_in_out']['in_frame']:
                    self.preview_in_frame_slot.emit('source', preview_window['frame_in_out']['in_frame'])
                if preview_window['frame_in_out']['out_frame']:
                    self.preview_out_frame_slot.emit('source', preview_window['frame_in_out']['out_frame'])
                self.jump_frame_slot.emit(preview_window['name'], preview_window['frame_no'])

        if 'source' not in self.preview_windows:
            self.new_preview_slot.emit('source')

        all_timelines = self.table_timelines.all()
        for timeline in all_timelines:
            for clip in timeline['clips']:
                db_frame_in_out = clip['frame_in_out']
                self.add_timeline_clip_slot.emit({
                    "source": QUrl(clip['source']),
                    "frame_in_out": FrameInOut(db_frame_in_out['in_frame'], db_frame_in_out['out_frame']),
                })

    @pyqtSlot(str, QUrl)
    def __on_update_preview_file(self, name, file):
        cap = cv2.VideoCapture(file.path())
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        new_dict1 = {
            **self.preview_windows[name],
            'video_file': file,
            'video_details': {
                'fps': fps,
                'total_frames': total_frames,
            },
            'frame_no': 0,
            'frame_in_out': FrameInOut(),
            'speed': 0,
        }

        new_dict = {
            **self.preview_windows,
            name: new_dict1,
        }
        self.preview_windows = new_dict
        print(self.preview_windows)

        self.change_speed_slot.emit('source', int(1000 / fps) + 1)

    def __change_speed_handler(self, name, speed):
        new_dict1 = {
            **self.preview_windows[name],
            'speed': speed,
        }

        new_dict = {
            **self.preview_windows,
            name: new_dict1,
        }
        self.preview_windows = new_dict
        print(self.preview_windows)

    @pyqtSlot(str)
    def __on_new_preview(self, name):
        if name not in self.preview_windows.keys():
            print(f'new preview window {name}')
            new_dict1 = {
                'video_file': None,
                'frame_no': 0,
                'frame_in_out': FrameInOut()
            }

            new_dict = {
                **self.preview_windows,
                name: new_dict1,
            }
            self.preview_windows = new_dict
            print(self.preview_windows)
        else:
            raise Exception(f"duplicate preview window {name}")

    @pyqtSlot(str)
    def __on_new_file(self, file):
        print('on new file')

        if len([x for x in self.files if x['file_path'] == file]) == 0:
            print(f'not duplicate {file}')
            cap = cv2.VideoCapture(file)
            data = {
                'file_path': file,
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            }
            cap.release()
            self.files = self.files + [data]
            self.new_file_added_slot.emit(file)

    @pyqtSlot()
    def __save_file(self):

        print('save it')
        # todo msg box to select save file

        self.table_files.truncate()

        for i, file in enumerate(self.files):
            self.table_files.insert({
                'file_path': file['file_path'],
                'order': i+1,
            })

        self.table_preview_windows.truncate()
        self.table_preview_windows.insert({
            'name': 'source',
            'video_file': self.__file_path_to_url(self.preview_windows['source']['video_file']),
            'frame_no': self.preview_windows['source']['frame_no'],
            'frame_in_out': asdict(self.preview_windows['source']['frame_in_out']),
        })

        self.table_timelines.truncate()
        self.table_timelines.insert({
            'name': 'default',
            'clips': [self.__timeline_clip_to_db_dict(clip) for clip in self.timeline['clips']],
        })

    def __timeline_clip_to_db_dict(self, timeline_clip: dict):
        return {
            "source": timeline_clip['source'].path(),
            "frame_in_out": asdict(timeline_clip['frame_in_out'])
        }

    def __file_path_to_url(self, url_file_path: QUrl) -> str:
        if url_file_path:
            return url_file_path.url()
        else:
            return None
