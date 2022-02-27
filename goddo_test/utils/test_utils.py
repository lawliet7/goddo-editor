import math
import time
from typing import Callable

import cv2
import numpy as np
from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QDrag, QImage
from PyQt5.QtWidgets import QApplication, QListWidget

from goddo_player.utils.url_utils import file_to_url
from goddo_test.utils.path_util import path_to_str, assets_folder_path


def grab_screenshot():
    screen = QApplication.primaryScreen()
    return screen.grabWindow(0).toImage()


def save_screenshot(file_name: str, img: QImage = None):

    if img is None:
        screen = QApplication.primaryScreen()
        img = screen.grabWindow(0).toImage()

    screenshot_name = path_to_str(assets_folder_path().joinpath(".output").joinpath(file_name))
    img.save(screenshot_name)


# wait for screenshot to finish loading
def wait_for_threadpool_to_complete(qtbot, threadpool):
    def check_no_more_threads_running():
        assert threadpool.activeThreadCount() == 0

    qtbot.waitUntil(check_no_more_threads_running, timeout=10000)


def grab_all_window_imgs(windows_tuple):
    screen = QApplication.primaryScreen()
    screen_img = screen.grabWindow(0).toImage()
    return [screen_img.copy(x.geometry()) for x in windows_tuple]


def cmp_image(img1, img2):
    res = cv2.matchTemplate(qimg_to_arr(img1), qimg_to_arr(img2), cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print('{}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))
    return max_val


def qimg_to_arr(img):
    num_of_channels = 4
    h = img.height()
    w = img.width()

    b = img.bits()
    b.setsize(h * w * num_of_channels)

    arr = np.frombuffer(b, np.uint8).reshape((h, w, num_of_channels))

    return arr


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
        print(f'got val {ret_val}')
        if ret_val:
            print('wait complete')
            return
        else:
            print(f'still waiting')
            time.sleep(check_interval_secs)
            
    raise Exception(f'wait timed out in {timeout_secs} secs')
