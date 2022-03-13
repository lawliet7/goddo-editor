import logging
import sys
import threading

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

from goddo_player.app.monarch import MonarchSystem
from goddo_test.utils.command_widget import CommandWidget


class QtAppThread(QObject):
    def __init__(self) -> None:
        super().__init__()

        self.app: QApplication = None
        self.mon: MonarchSystem = None
        self.cmd: CommandWidget = None

        self._t = threading.Thread(target=self.thread_function, args=())
        self._t.setName('God-Thread')
        self._t.setDaemon(True)

    def thread_function(self):
        try:
            logging.info('starting application in thread')
            self.app = QApplication(sys.argv)
            self.mon = MonarchSystem(self.app)

            self.cmd = CommandWidget(self.mon)

            sys.exit(self.app.exec())
        except SystemExit as s:
            logging.info(f'system exited with return code {s.code}')
            if s.code != 0:
                raise s
        except Exception as e:
            logging.info(e)
            raise e
        finally:
            logging.info('system is done')

    def start(self):
        self._t.start()

    def stop(self):
        logging.info(f'is thread alive {self._t.is_alive()}')
        self.app.quit()
        logging.info('app quit, waiting for thread to finish')
        self._t.join()
        logging.info('thread finished')
