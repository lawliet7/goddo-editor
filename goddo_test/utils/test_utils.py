import logging
import math
import os
import time
from copy import deepcopy
from typing import Callable

import cv2
import numpy as np
import pyautogui
from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QListWidget

from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.video_path import VideoPath
from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.utils.path_util import path_to_str, my_test_output_folder_path, video_folder_path


def grab_screenshot(region_tuple=None):
    if region_tuple:
        return pyautogui.screenshot(region=region_tuple)
    else:
        return pyautogui.screenshot()


# img is a pil image in windows
def save_screenshot(file_name: str, img=None):
    ext = os.path.splitext(file_name)[1]
    if ext not in ['.png', '.jpg']:
        raise Exception(f"sorry we don't support {ext} we only support png and jpg for screenshot format")

    if img is None:
        img = pil_img_to_arr(pyautogui.screenshot())

    screenshot_name = path_to_str(my_test_output_folder_path().joinpath(file_name))
    cv2.imwrite(screenshot_name, img)
    logging.info(f'created screenshot {screenshot_name}')

    if not os.path.exists(screenshot_name):
        raise Exception(f'failed to create screenshot {screenshot_name}')


# wait for screenshot to finish loading
def wait_for_threadpool_to_complete(qtbot, threadpool):
    def check_no_more_threads_running():
        assert threadpool.activeThreadCount() == 0

    qtbot.waitUntil(check_no_more_threads_running, timeout=10000)


def grab_all_window_imgs(windows_dict):
    d = {}
    for k, v in windows_dict.items():
        s = grab_screenshot(v.geometry().getRect())
        img = pil_img_to_arr(s)
        d[k] = img
    return d


# todo: test in ubuntu if img type will be different
def cmp_image(img1, img2):
    res = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    logging.info('{}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))
    return max_val


def qimg_to_arr(img):
    num_of_channels = 4
    h = img.height()
    w = img.width()

    b = img.bits()
    b.setsize(h * w * num_of_channels)

    arr = np.frombuffer(b, np.uint8).reshape((h, w, num_of_channels))

    return arr


def pil_img_to_arr(img):
    np_img = np.asarray(img)
    np_img = np_img[:, :, ::-1].copy()
    return deepcopy(np_img)


def list_widget_to_test_drag_and_drop(show=True):
    list_widget = QListWidget()

    def on_item_clicked(item):
        path = list_widget.itemWidget(item).text()

        drag = QDrag(list_widget)
        mime_data = QMimeData()
        mime_data.setUrls([file_to_url(path)])
        drag.setMimeData(mime_data)
        drag.exec()

    list_widget.itemPressed.connect(on_item_clicked)

    if show:
        list_widget.show()

    return list_widget


def wait_until(func: Callable[[], bool], check_interval_secs=0.5, timeout_secs=10):
    itr = int(math.ceil(timeout_secs / check_interval_secs))

    for i in range(itr):
        ret_val = func()
        logging.info(f'got val {ret_val}')
        if ret_val:
            logging.info('wait complete')
            return
        else:
            logging.info(f'still waiting')
            time.sleep(check_interval_secs)

    raise Exception(f'wait timed out in {timeout_secs} secs')


def drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y):
    pyautogui.moveTo(src_pt_x, src_pt_y)
    pyautogui.mouseDown()
    pyautogui.dragTo(dest_pt_x, dest_pt_y, duration=1)
    pyautogui.mouseUp()


def get_test_vid_path():
    file_path = video_folder_path().joinpath('supported').joinpath("test_vid.mp4").resolve()
    return VideoPath(file_to_url(file_path))


def click_on_prev_wind_slider(preview_window, pct, should_slider_value_change=True):
    slider = preview_window.slider

    old_slider_value = slider.value()

    pos = local_to_global_pos(slider, preview_window)
    x_offset = int(slider.width() * pct)
    y_offset = int(slider.height() * 0.5)
    pyautogui.moveTo(pos.x() + x_offset, pos.y() + y_offset)
    pyautogui.click()

    if should_slider_value_change:
        wait_until(lambda: slider.value() != old_slider_value)
    else:
        time.sleep(0.5)


def save_reload_and_assert_state(app_thread, windows_container, save_file_name: str):
    from goddo_test.utils.command_widget import Command, CommandType

    save_file_path = my_test_output_folder_path().joinpath(save_file_name).resolve()
    save_path = VideoPath(file_to_url(str(save_file_path)))

    state_dict = app_thread.mon.state.as_dict()

    app_thread.cmd.submit_cmd(Command(CommandType.SAVE_FILE, [save_path]))
    app_thread.cmd.submit_cmd(Command(CommandType.RESET))
    wait_until(lambda: windows_container.preview_window.preview_widget.cap is None)
    app_thread.cmd.submit_cmd(Command(CommandType.LOAD_FILE, [save_path]))
    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)

    after_load_state_dict = app_thread.mon.state.as_dict()

    assert after_load_state_dict['cur_save_file'] == str(save_path)

    # the save file is obviously going to be different since we jus loaded a brand new file
    state_dict.pop('cur_save_file')
    after_load_state_dict.pop('cur_save_file')

    # without this it's very hard to see which field has error
    for k in state_dict:
        assert state_dict[k] == after_load_state_dict[k], f'{k} is different'
    assert state_dict == after_load_state_dict
