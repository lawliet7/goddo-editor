import argparse
import logging
import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtWidgets import QApplication

from goddo_player.file_list import FileListWidget, FileList
from goddo_player.preview_window import PreviewWindow
from goddo_player.state_store import StateStore, StateStoreSignals


class MonarchSystem(QObject):
    def __init__(self, app: 'QApplication'):
        super().__init__()

        self.app = app
        self.state = StateStore()

        self.preview_window = PreviewWindow()
        self.preview_window.show()

        self.file_list = FileList()
        self.file_list.show()

        signals: StateStoreSignals = StateStoreSignals()
        signals.switch_preview_video_slot.connect(self.__on_update_preview_file)
        signals.update_preview_file_details_slot.connect(self.__on_update_preview_file_details)
        signals.add_file_slot.connect(self.__on_add_file)
        signals.save_slot.connect(self.__on_save_file)
        signals.load_slot.connect(self.__on_load_file)

    def __on_update_preview_file(self, url: 'QUrl', should_play: bool):
        logging.info('update preview file')
        self.state.preview_window.video_url = url
        self.preview_window.switch_video(self.state.preview_window.video_url)
        if should_play:
            self.preview_window.toggle_play_pause()

    def __on_update_preview_file_details(self, fps: float, total_frames: int):
        self.state.preview_window.fps = fps
        self.state.preview_window.total_frames = total_frames

    def __on_add_file(self, url: 'QUrl'):
        item = self.state.file_list.create_file_item(url)
        self.state.file_list.add_file_item(item)
        print(self.state.file_list)
        self.file_list.add_video(item.name)

    def __on_save_file(self, url: QUrl):
        self.state.save_file(url)

    def __on_load_file(self, url: QUrl):
        def handle_file_fn(file_dict):
            StateStoreSignals().add_file_slot.emit(QUrl.fromLocalFile(file_dict['name']))

        def handle_prev_wind_fn(prev_wind_dict):
            StateStoreSignals().switch_preview_video_slot.emit(QUrl.fromLocalFile(prev_wind_dict['video_url']), False)

        self.state.load_file(url, handle_file_fn, handle_prev_wind_fn)


def convert_to_log_level(log_level_str: str):
    if log_level_str:
        return logging.getLevelName(log_level_str.upper())
    else:
        return None


def main():
    parser = argparse.ArgumentParser(description="Goddo Serenade's video editor")
    parser.add_argument('--log-level', help='FATAL,ERROR,WARN,INFO,DEBUG, default is INFO')

    args = parser.parse_args()
    print(args)

    log_level = convert_to_log_level(args.log_level) or logging.INFO
    logging.basicConfig(format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(module)s.%(funcName)s - %(message)s', level=log_level)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.jpg'))

    monarch = MonarchSystem(app)

    url = QUrl.fromLocalFile(os.path.abspath(os.path.join('..', 'saves', 'a.json')))
    StateStoreSignals().load_slot.emit(url)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
