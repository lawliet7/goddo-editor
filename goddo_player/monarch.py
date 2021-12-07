import argparse
import logging
import os
import pathlib
import sys

from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from goddo_player.file_list import FileList
from goddo_player.preview_window import PreviewWindow
from goddo_player.signals import StateStoreSignals, PlayCommand
from goddo_player.state_store import StateStore
from goddo_player.ui.timeline_window2 import TimelineWindow2


class MonarchSystem(QObject):
    def __init__(self, app: 'QApplication'):
        super().__init__()

        self.app = app
        self.state = StateStore()

        self.file_list = FileList()
        self.file_list.show()

        left = self.file_list.geometry().left() + 50
        top = self.file_list.geometry().top() + 20

        self.preview_window = PreviewWindow()
        self.preview_window.show()
        self.preview_window.move(left, top)

        self.timeline_window = TimelineWindow2()
        self.timeline_window.show()
        self.timeline_window.move(left, self.preview_window.geometry().bottom() + 10)

        self.signals: StateStoreSignals = StateStoreSignals()
        self.signals.switch_preview_video_slot.connect(self.__on_update_preview_file)
        self.signals.update_preview_file_details_slot.connect(self.__on_update_preview_file_details)
        self.signals.add_file_slot.connect(self.__on_add_file)
        self.signals.save_slot.connect(self.__on_save_file)
        self.signals.load_slot.connect(self.__on_load_file)
        self.signals.preview_video_in_frame_slot.connect(self.__on_preview_video_in_frame_slot)
        self.signals.preview_video_out_frame_slot.connect(self.__on_preview_video_out_frame_slot)
        self.signals.preview_window_play_cmd_slot.connect(self.__on_preview_window_play_cmd_slot)

    def __on_update_preview_file(self, url: 'QUrl', should_play: bool):
        logging.info('update preview file')
        self.state.preview_window.video_url = url
        self.preview_window.switch_video(self.state.preview_window.video_url)
        if should_play:
            self.signals.preview_window_play_cmd_slot.emit(PlayCommand.PLAY)
        self.preview_window.activateWindow()

    def __on_update_preview_file_details(self, fps: float, total_frames: int):
        self.state.preview_window.fps = fps
        self.state.preview_window.total_frames = total_frames

    def __on_add_file(self, url: 'QUrl'):
        item = self.state.file_list.create_file_item(url)
        self.state.file_list.add_file_item(item)
        self.file_list.add_video(item.name)

    def __on_save_file(self, url: QUrl):
        self.state.save_file(url)

    def __on_load_file(self, url: QUrl):
        def handle_file_fn(file_dict):
            StateStoreSignals().add_file_slot.emit(QUrl.fromLocalFile(file_dict['name']))

        def handle_prev_wind_fn(prev_wind_dict):
            StateStoreSignals().switch_preview_video_slot.emit(QUrl.fromLocalFile(prev_wind_dict['video_url']), False)
            logging.debug(f"loading in out {prev_wind_dict['frame_in_out']}")
            if prev_wind_dict['frame_in_out']['in_frame'] is not None:
                StateStoreSignals().preview_video_in_frame_slot.emit(prev_wind_dict['frame_in_out']['in_frame'])
            if prev_wind_dict['frame_in_out']['out_frame'] is not None:
                StateStoreSignals().preview_video_out_frame_slot.emit(prev_wind_dict['frame_in_out']['out_frame'])

        self.state.load_file(url, handle_file_fn, handle_prev_wind_fn)

    def __on_preview_video_in_frame_slot(self, pos: int):
        logging.info(f'update in frame to {pos}')
        self.state.preview_window.frame_in_out = self.state.preview_window.frame_in_out.update_in_frame(pos)

    def __on_preview_video_out_frame_slot(self, pos: int):
        logging.info(f'update out frame to {pos}')
        self.state.preview_window.frame_in_out = self.state.preview_window.frame_in_out.update_out_frame(pos)

    def __on_preview_window_play_cmd_slot(self, play_cmd: PlayCommand):
        self.preview_window.toggle_play_pause(play_cmd)


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

    local_save_path = os.path.abspath(os.path.join('..', 'saves', 'a.json'))
    if pathlib.Path(local_save_path).resolve().exists():
        url = QUrl.fromLocalFile(local_save_path)
        StateStoreSignals().load_slot.emit(url)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
