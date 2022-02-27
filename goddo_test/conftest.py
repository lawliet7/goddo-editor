import sys
import threading

import pytest
from PyQt5.QtWidgets import QApplication, QWidget

from goddo_player.app.monarch import MonarchSystem
from goddo_test.utils.test_utils import wait_until


class QtAppThread:

    def __init__(self) -> None:
        super().__init__()

        self.app: QApplication = None
        self.mon: MonarchSystem = None

        self.t = threading.Thread(target=self.thread_function, args=())
        self.t.setDaemon(True)

    def thread_function(self):
        try:
            self.app = QApplication(sys.argv)
            self.mon = MonarchSystem(self.app)
            sys.exit(self.app.exec())
        except SystemExit as s:
            print(f'system exited with return code {s.code}')

    def start(self):
        self.t.start()

    def stop(self):
        self.app.quit()


@pytest.fixture()
def app_thread():
    t = QtAppThread()
    t.start()

    wait_until(lambda: t.mon is not None)

    yield t
    t.stop()
    print('stop')
