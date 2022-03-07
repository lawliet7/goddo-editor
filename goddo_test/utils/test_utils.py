import logging
import math
import time
from copy import deepcopy
from typing import Callable

import cv2
import numpy as np
import pyautogui
from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QDrag, QImage
from PyQt5.QtWidgets import QApplication, QListWidget

from goddo_player.utils.url_utils import file_to_url
from goddo_test.utils.path_util import path_to_str, output_screenshot_folder_path


def grab_screenshot(region_tuple=None):
    if region_tuple:
        return pyautogui.screenshot(region=region_tuple)
    else:
        return pyautogui.screenshot()


# img is a pil image in windows
def save_screenshot(file_name: str, img=None):
    if img is None:
        img = pil_img_to_arr(pyautogui.screenshot())

    screenshot_name = path_to_str(output_screenshot_folder_path().joinpath(file_name))
    cv2.imwrite(screenshot_name, img)


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
