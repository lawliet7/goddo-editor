import logging
import time

import pyautogui
import pytest
from PyQt5.QtWidgets import QWidget, QApplication

from goddo_test.utils.QtAppThread import QtAppThread
from goddo_test.utils.command_widget import Command
from goddo_test.utils.path_util import output_screenshot_folder_path
from goddo_test.utils.test_utils import wait_until, grab_all_window_imgs, cmp_image, save_screenshot


def test_all_visible(app_thread):
    assert app_thread.mon.tabbed_list_window.isVisible()
    assert app_thread.mon.preview_window.isVisible()
    assert app_thread.mon.preview_window_output.isVisible()
    assert app_thread.mon.timeline_window.isVisible()

    # time.sleep(10)

    # cleanup
    wait_until(lambda: app_thread.cmd.queue_is_empty())


def np_arr_to_1d_list(np_arr):
    data = []
    d1, d2, d3 = np_arr.shape
    for i in range(d1):
        for j in range(d2):
            for k in range(d3):
                data.append(np_arr[i][j][k])
    return data


@pytest.mark.parametrize("test_win_key", ['TABBED_LIST_WINDOW', 'PREVIEW_WINDOW', 'OUTPUT_WINDOW', 'TIMELINE_WINDOW'])
# @pytest.mark.parametrize("test_win_key", ['TABBED_LIST_WINDOW'])
def test_show_all_file_window_main(app_thread, windows_dict, test_win_key, comparison_threshold=0.9):
    submit_cmd = app_thread.cmd.submit_cmd

    # img = pyautogui.screenshot()
    # img.save(str(output_screenshot_folder_path().joinpath('test_screenshot.png').resolve()))

    img_base_windows_dict = grab_all_window_imgs(windows_dict)
    logging.fatal(type(img_base_windows_dict['TABBED_LIST_WINDOW']))

    # (1000, 546, 3)
    d1 = np_arr_to_1d_list(img_base_windows_dict['TABBED_LIST_WINDOW'])

    for win_name, img in img_base_windows_dict.items():
        save_screenshot(f'visibility_cmp_{win_name}_base.png', img)

    submit_cmd(Command.SHOW_MAX_WINDOW)
    submit_cmd(getattr(Command, f'ACTIVATE_{test_win_key}'))

    wait_until(lambda: windows_dict[test_win_key].isActiveWindow())

    # time.sleep(1)

    img_new_windows_dict = grab_all_window_imgs(windows_dict)

    d2 = np_arr_to_1d_list(img_base_windows_dict['TABBED_LIST_WINDOW'])
    assert d1 == d2

    for k in windows_dict.keys():
        new_img = img_new_windows_dict[k]
        base_img = img_base_windows_dict[k]
        save_screenshot(f'visibility_cmp_before_win_{test_win_key}_{k}_new.png', new_img)
        save_screenshot(f'visibility_cmp_before_win_{test_win_key}_{k}_base.png', base_img)
        if k == test_win_key:
            assert cmp_image(new_img, base_img) > comparison_threshold, f'failed for {test_win_key} - {k}'
        else:
            assert cmp_image(new_img, base_img) < comparison_threshold, f'failed for {test_win_key} - {k}'

    pyautogui.press('F2')

    img_new_windows_dict = grab_all_window_imgs(windows_dict)

    d3 = np_arr_to_1d_list(img_base_windows_dict['TABBED_LIST_WINDOW'])
    assert d1 == d3

    for k in windows_dict.keys():
        new_img = img_new_windows_dict[k]
        base_img = img_base_windows_dict[k]
        save_screenshot(f'visibility_cmp_after_win_{test_win_key}_{k}_new.png', new_img)
        save_screenshot(f'visibility_cmp_after_win_{test_win_key}_{k}_base.png', base_img)
        assert cmp_image(new_img, base_img) > comparison_threshold


