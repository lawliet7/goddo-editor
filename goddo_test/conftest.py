import logging

import pytest

from goddo_player.app.monarch import MonarchSystem
from goddo_test.utils.QtAppThread import QtAppThread
from goddo_test.utils.test_utils import wait_until


@pytest.fixture(scope='session')
def app_thread():
    t = QtAppThread()
    t.start()

    wait_until(lambda: t.mon is not None)

    # t.mon.tabbed_list_window.activateWindow()
    # t.mon.preview_window.activateWindow()
    # t.mon.preview_window_output.activateWindow()
    # t.mon.timeline_window.activateWindow()

    yield t
    logging.info('stopping thread')
    t.stop()
    logging.info('stop')
