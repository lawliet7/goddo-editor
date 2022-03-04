import time

import pyautogui
import pytest
from PyQt5.QtWidgets import QWidget

from goddo_test.utils.QtAppThread import QtAppThread
from goddo_test.utils.command_widget import Command
from goddo_test.utils.test_utils import wait_until, grab_all_window_imgs, cmp_image, save_screenshot


def test_all_visible(app_thread):
    assert app_thread.mon.tabbed_list_window.isVisible()
    assert app_thread.mon.preview_window.isVisible()
    assert app_thread.mon.preview_window_output.isVisible()
    assert app_thread.mon.timeline_window.isVisible()

    # time.sleep(10)

    # cleanup
    wait_until(lambda: app_thread.cmd.queue_is_empty())


def test_show_all_file_window_main(app_thread):
    idx = 0
    comparison_threshold = 0.9
    submit_cmd = app_thread.cmd.submit_cmd

    windows_tuple = (app_thread.mon.tabbed_list_window, app_thread.mon.preview_window,
                     app_thread.mon.preview_window_output, app_thread.mon.timeline_window)

    img_base_windows = grab_all_window_imgs(windows_tuple)

    submit_cmd(Command.SHOW_MAX_WINDOW)
    submit_cmd(Command.ACTIVATE_FILE_WINDOW)

    wait_until(lambda: app_thread.cmd.queue_is_empty())

    img_new_windows = grab_all_window_imgs(windows_tuple)

    for i in range(len(windows_tuple)):
        if i == idx:
            assert cmp_image(img_new_windows[i], img_base_windows[i]) > comparison_threshold
        else:
            assert cmp_image(img_new_windows[i], img_base_windows[i]) < comparison_threshold

    pyautogui.press('F2')

    img_new_windows = grab_all_window_imgs(windows_tuple)

    for i in range(len(windows_tuple)):
        save_screenshot(f'visibility_win_{i}_new.png', img_new_windows[i])
        save_screenshot(f'visibility_win_{i}_base.png', img_new_windows[i])
        assert cmp_image(img_new_windows[i], img_base_windows[i]) > comparison_threshold


