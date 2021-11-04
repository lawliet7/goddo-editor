from PyQt5.QtCore import QObject, pyqtSignal, QUrl, pyqtSlot

from goddo_player.ui.func_collection_utils import copy_and_add_to_dict
from goddo_player.ui.singleton_meta import singleton


@singleton
class State(QObject):
    update_preview_file_slot = pyqtSignal(str, QUrl)
    new_preview_slot = pyqtSignal(str)
    new_file_slot = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # print(f'save file {save_file}')
        # is_existing_file = pathlib.Path(self.save_file).resolve().exists()

        # self.db = TinyDB(self.save_file)
        # video_table = self.db.table('videos')

        self.preview_windows = {}
        self.files = []

        # self.preview_windows = [{
        #     "video_file": None
        # }]
        # video_table.all()

        self.update_preview_file_slot.connect(self.__on_update_preview_file)
        self.new_preview_slot.connect(self.__on_new_preview)
        self.new_file_slot.connect(self.__on_new_file)

    def load_save(self, save_file):
        pass

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
        if file not in self.files:
            self.files = self.files + [file]

    def save_state(self):
        pass
