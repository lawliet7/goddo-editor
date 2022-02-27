import math
import sys
import threading
import time
from typing import Callable

import pytest
from PyQt5.QtWidgets import QApplication

from goddo_player.app.monarch import MonarchSystem


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


def wait_until(func: Callable[[], bool], check_interval_secs=0.5, timeout_secs=10):
    itr = int(math.ceil(timeout_secs / check_interval_secs))

    for i in range(itr):
        ret_val = func()
        print(f'got val {ret_val}')
        if ret_val:
            print('wait complete')
            break
        else:
            print(f'still waiting')
            time.sleep(check_interval_secs)


@pytest.fixture()
def app_thread():
    t = QtAppThread()
    t.start()

    def check():
        return t.mon is not None

    wait_until(check)

    yield t
    t.stop()
    print('stop')


def test_all_visible(app_thread):
    assert app_thread.mon.tabbed_list_window.isVisible()
    assert app_thread.mon.preview_window.isVisible()
    assert app_thread.mon.preview_window_output.isVisible()
    assert app_thread.mon.timeline_window.isVisible()
