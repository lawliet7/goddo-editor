import argparse
import logging
import os
import pathlib
import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from goddo_player.monarch import MonarchSystem
from goddo_player.signals import StateStoreSignals


def convert_to_log_level(log_level_str: str):
    if log_level_str:
        return logging.getLevelName(log_level_str.upper())
    else:
        return None


def main():
    parser = argparse.ArgumentParser(description="Goddo Serenade's video editor")
    parser.add_argument('--log-level', help='FATAL,ERROR,WARN,INFO,DEBUG, default is INFO')

    args = parser.parse_args()
    logging.info(args)

    log_level = convert_to_log_level(args.log_level) or logging.INFO
    logging.basicConfig(format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(module)s.%(funcName)s - %(message)s',
                        level=log_level)

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