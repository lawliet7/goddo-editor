import logging
import os

import pytest


# import os
# logging.info(os.environ.get("PATH"))
# os.environ["PATH"] = f'C:\Users\William\Anaconda3\envs\goddo-editor;C:\Users\William\Anaconda3\envs\goddo-editor\Library\mingw-w64\bin;C:\Users\William\Anaconda3\envs\goddo-editor\Library\usr\bin;C:\Users\William\Anaconda3\envs\goddo-editor\Library\bin;C:\Users\William\Anaconda3\envs\goddo-editor\Scripts;C:\Users\William\Anaconda3\envs\goddo-editor\bin;C:\Users\William\Anaconda3\condabin;C:\Program Files (x86)\Intel\iCLS Client;C:\Program Files\Intel\iCLS Client;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0;C:\Program Files (x86)\Intel\Intel(R) Management Engine Components\DAL;C:\Program Files\Intel\Intel(R) Management Engine Components\DAL;C:\Program Files (x86)\Intel\Intel(R) Management Engine Components\IPT;C:\Program Files\Intel\Intel(R) Management Engine Components\IPT;C:\Program Files\Intel\WiFi\bin;C:\Program Files\Common Files\Intel\WirelessCommon;C:\WINDOWS\System32\OpenSSH;C:\Program Files\Git\cmd;C:\Users\William\AppData\Local\Microsoft\WindowsApps;C:\Users\William\dev\ffmpeg-2021-06-13-git-3ce272a9da-full_build\bin;.'

from goddo_test.utils.qt_app_thread import QtAppThread
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import my_test_output_folder_path, list_files
from goddo_test.utils.test_utils import wait_until
from goddo_test.utils.windows_container import WindowsContainer


pytest.register_assert_rewrite('goddo_test.common_asserts')


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


