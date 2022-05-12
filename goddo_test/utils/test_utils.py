import inspect
import logging
import math
import os
import time
from copy import deepcopy
from typing import Callable, List

import cv2
import numpy as np
import pyautogui
from PyQt5.QtCore import QMimeData, QRect, QSize
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QListWidget
from goddo_player.app.state_store import TimelineClip
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.time_frame_utils import time_str_to_components

from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.video_path import VideoPath
from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.utils.path_util import image_folder_path, path_to_str, my_test_output_folder_path, video_folder_path


def grab_screenshot(region_tuple=None):
    if region_tuple:
        return pil_img_to_arr(pyautogui.screenshot(region=region_tuple))
    else:
        return pil_img_to_arr(pyautogui.screenshot())


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
def cmp_image(baseImg, templateImg) -> float:
    res = cv2.matchTemplate(baseImg, templateImg, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    logging.info('{}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))
    return max_val

def get_img_asset(file_name):
    return cv2.imread(str(image_folder_path().joinpath(file_name).resolve()), cv2.COLOR_BGR2RGB)

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


def get_test_vid_path(ext='mp4'):
    file_path = video_folder_path().joinpath('supported').joinpath(f"test_vid.{ext}").resolve()
    return VideoPath(file_to_url(file_path))

def get_test_vid_2_path():
    file_path = video_folder_path().joinpath("test_vid2.mp4").resolve()
    return VideoPath(file_to_url(file_path))

# generated via this cmd:
# ffmpeg -t 900 -f lavfi -i color=c=green:s=640x360 -c:v libx264 -tune stillimage -pix_fmt yuv420p -r 24 blank_15m_vid.mp4
def get_blank_15m_vid_path():
    file_path = video_folder_path().joinpath("blank_15m_vid.mp4").resolve()
    return VideoPath(file_to_url(file_path))

def get_blank_1hr_vid_path():
    file_path = video_folder_path().joinpath("blank_1hr_vid.mp4").resolve()
    return VideoPath(file_to_url(file_path))

def get_timeline_clip_for_1hr_vid(in_frame=None, out_frame=None):
    return TimelineClip(get_blank_1hr_vid_path(), 4.0, 14402, FrameInOut(in_frame,out_frame))

def get_timeline_clip_for_15m_vid(in_frame=None, out_frame=None):
    return TimelineClip(get_blank_15m_vid_path(), 24.0, 21602, FrameInOut(in_frame,out_frame))

def click_on_prev_wind_slider(preview_window, pct: float, should_slider_value_change: bool=True):
    old_frame_no = preview_window.state.preview_window.current_frame_no
    
    go_to_prev_wind_slider(preview_window, pct)
    pyautogui.click()

    if should_slider_value_change:
        wait_until(lambda: old_frame_no != preview_window.state.preview_window.current_frame_no)
    else:
        time.sleep(0.5)

def go_to_prev_wind_slider(preview_window, pct):
    slider = preview_window.slider
    pos = local_to_global_pos(slider, preview_window)
    x_offset = int(slider.width() * pct)
    y_offset = int(slider.height() * 0.5)
    pyautogui.moveTo(pos.x() + x_offset, pos.y() + y_offset)


def save_reload_and_assert_state(app_thread, windows_container, blank_state, save_file_name: str):
    from goddo_test.utils.command_widget import Command, CommandType

    save_file_path = my_test_output_folder_path().joinpath(save_file_name).resolve()
    save_path = VideoPath(file_to_url(str(save_file_path)))

    before_state_dict = app_thread.mon.state.as_dict()
    before_win_state_dict = windows_container.as_dict()

    if windows_container.output_window.preview_widget.cap is not None:
        check_type = "output_window"
    elif len(windows_container.timeline_window.inner_widget.clip_rects) > 0:
        check_type = 'timeline_window'
    elif windows_container.preview_window.preview_widget.cap is not None:
        check_type = "preview_window"
    elif windows_container.tabbed_list_window.videos_tab.list_widget.count() > 0:
        check_type = "file_list_window"
    else:
        check_type = None

    app_thread.cmd.submit_cmd(Command(CommandType.SAVE_FILE, [save_path]))
    app_thread.cmd.submit_cmd(Command(CommandType.RESET))
    wait_until(lambda: windows_container.preview_window.preview_widget.cap is None)

    time.sleep(0.5)

    reset_state_dict = app_thread.mon.state.as_dict()
    assert_state(reset_state_dict, blank_state)

    app_thread.cmd.submit_cmd(Command(CommandType.LOAD_FILE, [save_path]))
    if check_type == 'output_window':
        wait_until(lambda: len(windows_container.timeline_window.inner_widget.clip_rects) > 0)
    elif check_type == 'timeline_window':
        wait_until(lambda: len(windows_container.timeline_window.inner_widget.clip_rects) > 0)
    elif check_type == 'preview_window':
        wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)
    elif check_type == 'file_list_window':
        wait_until(lambda: windows_container.tabbed_list_window.videos_tab.list_widget.count() > 0)

    time.sleep(0.5)

    after_load_state_dict = app_thread.mon.state.as_dict()
    after_load_win_state_dict = windows_container.as_dict()

    logging.info(f'after_load_win_state_dict = {after_load_win_state_dict}')

    assert after_load_state_dict['cur_save_file'] == str(save_path)

    assert_state(before_state_dict, after_load_state_dict)
    assert_state(before_win_state_dict, after_load_win_state_dict)

def assert_state(src_state, dest_state, is_window_state=False):
    if not is_window_state:
        if 'cur_save_file' in src_state:
            src_state = src_state.copy()
            src_state.pop('cur_save_file')

        if 'cur_save_file' in dest_state:
            dest_state = dest_state.copy()
            dest_state.pop('cur_save_file')        
    
    for k in src_state:
        assert src_state[k] == dest_state[k], f'{k} is different'
    assert src_state == dest_state

def qrect_as_dict(rect: QRect):
    return {
        'x': rect.x(),
        'y': rect.y(),
        'width': rect.width(),
        'height': rect.height()
    }

def qsize_as_dict(size: QSize):
    return {
        'height': size.height(),
        'width': size.width()
    }

def drop_video_on_file_list(app_thread, windows_container, video_paths: List[VideoPath]):
    from goddo_test.utils.command_widget import Command, CommandType

    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    for video_path in video_paths:
        app_thread.cmd.submit_cmd(Command(CommandType.ADD_ITEM_DND_WINDOW, [video_path.str()]))    

    dnd_widget = app_thread.cmd.dnd_widget

    _, item_widget = dnd_widget.get_item_and_widget(0)

    src_corner_pt = dnd_widget.item_widget_pos(0)
    src_pt_x = src_corner_pt.x() + 10
    src_pt_y = src_corner_pt.y() + int(item_widget.size().height() / 2)

    videos_tab = windows_container.tabbed_list_window.videos_tab
    video_tab_list_widget = videos_tab.list_widget
    dest_corner_pt = local_to_global_pos(video_tab_list_widget, videos_tab)
    dest_pt_x = dest_corner_pt.x() + 10
    dest_pt_y = dest_corner_pt.y() + 10

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    wait_until(lambda: video_tab_list_widget.count() == len(video_paths))

def drop_video_on_preview(app_thread, windows_container, video_path):
    from goddo_test.utils.command_widget import Command, CommandType

    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    app_thread.cmd.submit_cmd(Command(CommandType.ADD_ITEM_DND_WINDOW, [video_path.str()]))

    dnd_widget = app_thread.cmd.dnd_widget

    item_idx = dnd_widget.get_count() - 1
    _, item_widget = dnd_widget.get_item_and_widget(item_idx)

    src_corner_pt = dnd_widget.item_widget_pos(item_idx)
    src_pt_x = src_corner_pt.x() + 10
    src_pt_y = src_corner_pt.y() + int(item_widget.size().height() / 2)

    dest_corner_pt = local_to_global_pos(windows_container.preview_window.preview_widget, windows_container.preview_window)
    dest_pt_x = dest_corner_pt.x() + 10
    dest_pt_y = dest_corner_pt.y() + 10

    # win_rect = windows_container.preview_window.geometry().getRect()
    # base_img = pil_img_to_arr(pyautogui.screenshot(region=win_rect))

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)

    pyautogui.press('space')

    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

def get_current_method_name(levels=1):
    cur_frame = inspect.currentframe()
    try:
        for _ in range(levels):
            cur_frame = cur_frame.f_back
        return inspect.getmodulename(cur_frame.f_code.co_filename), cur_frame.f_code.co_name
    finally:
        del cur_frame

def enter_time_in_go_to_dialog_box(app_thread, time_label: str, should_go_to_frame: bool = True):
    pyautogui.press('g')
    pyautogui.press('home')
    pyautogui.press('delete')
    logging.info(f'=== write 1 {time_label[0]}')
    pyautogui.typewrite(time_label[0])
    pyautogui.press('right')
    pyautogui.press('delete')
    pyautogui.press('delete')
    pyautogui.typewrite(time_label[2:4])
    pyautogui.press('right')
    pyautogui.press('delete')
    pyautogui.press('delete')
    pyautogui.typewrite(time_label[5:7])
    pyautogui.press('right')
    pyautogui.press('delete')
    pyautogui.press('delete')
    pyautogui.typewrite(time_label[-2:])

    if should_go_to_frame:
        pyautogui.press('enter')

        frame_no = app_thread.mon.preview_window.time_edit.value()
        wait_until(lambda: app_thread.mon.state.preview_window.current_frame_no == frame_no)
    else:
        wait_until(lambda: app_thread.mon.preview_window.time_edit.text() == time_label)

