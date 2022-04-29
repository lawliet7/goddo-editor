import logging
import os

import pytest

from goddo_test.utils.qt_app_thread import QtAppThread
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import my_test_output_folder_path, list_files
from goddo_test.utils.test_utils import wait_until
from goddo_test.utils.windows_container import WindowsContainer


pytest.register_assert_rewrite('goddo_test.common_asserts')
pytest.register_assert_rewrite('goddo_test.utils.assert_utils')


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


@pytest.fixture(scope='session')
def windows_container(app_thread):
    wc = WindowsContainer(
        app_thread.mon.tabbed_list_window,
        app_thread.mon.preview_window,
        app_thread.mon.preview_window_output,
        app_thread.mon.timeline_window,
    )
    for _, w in vars(wc).items():
        wait_until(lambda: w.isVisible())
    return wc


@pytest.fixture(autouse=True)
def ui_reset(app_thread):
    yield
    app_thread.cmd.submit_cmd(Command(CommandType.RESET))


@pytest.fixture(autouse=True, scope='session')
def image_folder():
    my_test_output_folder_path().mkdir(exist_ok=True)

    png_files = list_files(my_test_output_folder_path(), filter_func=lambda f: f.lower().endswith(".png") or f.lower().endswith(".json"))
    for p in png_files:
        logging.info(f'deleting {p}')
        os.remove(p)

    return

@pytest.fixture(scope='session')
def blank_state(app_thread, windows_container):
    d = app_thread.mon.state.as_dict()
    d.pop('cur_save_file')
    yield d


