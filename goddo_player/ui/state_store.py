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

    def __load_file(self, save_file):
        self.db = TinyDB(save_file)
        self.table_preview_windows: Table = self.db.table('preview_windows')
        self.table_files: Table = self.db.table('files')
        self.save_file = save_file

        all_files = self.table_files.all()
        print(all_files)
        for file in all_files:
            print(f'emitting file {file["file_path"]}')
            self.new_file_slot.emit(file["file_path"])

    @pyqtSlot(str, QUrl)
    def __on_update_preview_file(self, name, file):
        self.preview_windows = copy_and_add_to_dict(self.preview_windows,
                                                    name, copy_and_add_to_dict(self.preview_windows[name],
                                                                               'video_file', file))
        print(self.preview_windows)

    @pyqtSlot(str)
    def __on_new_preview(self, name):
        if name not in self.preview_windows.keys():
            print(f'new preview window {name}')
            self.preview_windows = copy_and_add_to_dict(self.preview_windows, name, {"video_file": None})
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
