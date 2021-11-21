import logging
import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

from goddo_player.preview_window import PreviewWindow
from goddo_player.state_store import StateStore, StateStoreSignals


class MonarchSystem(QObject):
    def __init__(self, app: 'QApplication'):
        super().__init__()

        self.app = app
        self.state = StateStore()
        self.preview_window = PreviewWindow()
        self.preview_window.show()

        signals = StateStoreSignals()
        signals.update_preview_file_slot.connect(self.__on_update_preview_file)

    def __on_update_preview_file(self, url: 'QUrl'):
        logging.info('update preview file')
        self.preview_window.switch_video(url)


def convert_to_log_level(log_level_str: str):
    if log_level_str:
        return logging.getLevelName(log_level_str.upper())
    else:
        return None


def main():

    log_level = convert_to_log_level(os.getenv('LOG_LEVEL')) or logging.INFO
    logging.basicConfig(format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s', level=log_level)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.jpg'))

    monarch = MonarchSystem(app)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
