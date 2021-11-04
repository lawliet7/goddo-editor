import os

from PyQt5.QtCore import QObject, pyqtSignal, QUrl, pyqtSlot
from tinydb import TinyDB, Query
from tinydb.table import Table

from goddo_player.ui.func_collection_utils import copy_and_add_to_dict
from goddo_player.ui.singleton_meta import singleton


@singleton
class State(QObject):
    update_preview_file_slot = pyqtSignal(str, QUrl)
    new_preview_slot = pyqtSignal(str)
    new_file_slot = pyqtSignal(str)
    load_slot = pyqtSignal(str)
    save_slot = pyqtSignal()
    play_slot = pyqtSignal(str)
    pause_slot = pyqtSignal(str)
    post_pause_slot = pyqtSignal(str, int)
    jump_frame_slot = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        # print(f'save file {save_file}')
        # is_existing_file = pathlib.Path(self.save_file).resolve().exists()

        self.save_file = None
        self.db = None
        self.table_preview_windows: Table = None
        self.table_files: Table = None
        # video_table = self.db.table('videos')

        self.preview_windows = {}
        self.files = []

        self.update_preview_file_slot.connect(self.__on_update_preview_file)
        self.new_preview_slot.connect(self.__on_new_preview)
        self.new_file_slot.connect(self.__on_new_file)
        self.load_slot.connect(self.__load_file)
        self.save_slot.connect(self.__save_file)
        self.post_pause_slot.connect(self.__post_pause_handler)

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
        self.save_file = save_file

        self.preview_windows = {}
        self.files = []

        all_files = self.table_files.all()
        print(all_files)
        for file in all_files:
            print(f'emitting file {file["file_path"]}')
            self.new_file_slot.emit(file["file_path"])

        all_preview_windows = self.table_preview_windows.all()
        for preview_window in all_preview_windows:
            print(f'preview {preview_window}')
            self.new_preview_slot.emit(preview_window['name'])
            self.update_preview_file_slot.emit(preview_window['name'], QUrl(preview_window['video_file']))
            self.jump_frame_slot.emit(preview_window['name'], preview_window['frame_no'])

        if 'source' not in self.preview_windows:
            self.new_preview_slot.emit('source')

    @pyqtSlot(str, QUrl)
    def __on_update_preview_file(self, name, file):
        new_dict1 = {
            **self.preview_windows[name],
            'video_file': file,
            'frame_no': 0,
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
            self.preview_windows = copy_and_add_to_dict(self.preview_windows, name, {"video_file": None, "frame_no": 0})
        else:
            raise Exception(f"duplicate preview window {name}")

    @pyqtSlot(str)
    def __on_new_file(self, file):
        print('on new file')
        if file not in self.files:
            self.files = self.files + [file]

    @pyqtSlot()
    def __save_file(self):
        print('save it')
        # todo msg box to select save file

        self.table_files.truncate()

        for i, file in enumerate(self.files):
            self.table_files.insert({
                'file_path': file,
                'order': i+1,
            })

        self.table_preview_windows.truncate()
        self.table_preview_windows.insert({
            'name': 'source',
            'video_file': self.preview_windows['source']['video_file'].url(),
            'frame_no': self.preview_windows['source']['frame_no'],
        })
