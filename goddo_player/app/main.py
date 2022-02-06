import argparse
import logging
import pathlib
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from goddo_player.app.monarch import MonarchSystem
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.utils.url_utils import file_to_url


def convert_to_log_level(log_level_str: str):
    if log_level_str:
        return logging.getLevelName(log_level_str.upper())
    else:
        return None


def main():
    parser = argparse.ArgumentParser(description="Goddo Serenade's video editor")
    parser.add_argument('--log-level', help='FATAL,ERROR,WARN,INFO,DEBUG, default is INFO')
    parser.add_argument('--save-file', help='Optional save file location')

    args = parser.parse_args()
    print(args)

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    log_level = convert_to_log_level(args.log_level) or logging.INFO
    logging.basicConfig(format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(module)s.%(funcName)s - %(message)s',
                        level=log_level)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(pathlib.Path(__file__).parent.joinpath('icon.jpg').resolve())))

    m = MonarchSystem(app)

    url = file_to_url(args.save_file) if args.save_file else file_to_url(PlayerConfigs.default_save_file)
    m.signals.load_slot.emit(url)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
