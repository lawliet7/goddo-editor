import logging
import re
import time

import pyautogui
import pytest
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QLabel
from goddo_player.utils.time_frame_utils import time_str_to_frames

from goddo_player.utils.video_path import VideoPath
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.common_asserts import assert_state_is_blank
from goddo_test.utils.assert_utils import assert_blank_timeline, generic_assert, get_assert_blank_list_fn, get_assert_file_list_for_test_file_1_fn, get_assert_preview_for_blank_file_fn, get_assert_preview_for_test_file_1_fn
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.test_utils import drag_and_drop, drop_video_on_file_list, enter_time_in_go_to_dialog_box, get_test_vid_path, wait_until, pil_img_to_arr, cmp_image
from goddo_test.utils.windows_container import WindowsContainer


def test_dbl_click_video_list(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_file_list(app_thread, windows_container, [video_path])

    new_total_count_expected = 1

    video_tab_list_widget = app_thread.mon.tabbed_list_window.videos_tab.list_widget
    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.list_widget.count() == new_total_count_expected)
    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.thread_pool.activeThreadCount() == 0)

    item = video_tab_list_widget.get_all_items()[0]
    item_widget = video_tab_list_widget.itemWidget(item)
    pt = local_to_global_pos(item_widget, video_tab_list_widget)
    pyautogui.moveTo(pt.x() + 10, pt.y() + 10)
    pyautogui.doubleClick()

    wait_until(lambda: windows_container.preview_window.preview_widget.frame_pixmap is not None)

    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())
    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.thread_pool.activeThreadCount() == 0)

    generic_assert(app_thread, windows_container, blank_state,
                   get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                   get_assert_preview_for_test_file_1_fn(), 
                   get_assert_preview_for_blank_file_fn(is_output_window=True), 
                   assert_blank_timeline)


def test_drop_on_preview_window(app_thread, windows_container: WindowsContainer, blank_state):
    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    video_path = get_test_vid_path()
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

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    wait_until(lambda: windows_container.preview_window.preview_widget.frame_pixmap is not None)

    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    frames_3_sec = int(round(29.97 * 3))

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.42, 0.43), current_frame_no=frames_3_sec),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_open_video_already_in_file_list(app_thread, windows_container, blank_state):
    video_path1 = get_test_vid_path()
    drop_video_on_file_list(app_thread, windows_container, [video_path1])
    
    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    video_path = get_test_vid_path()
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

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    wait_until(lambda: app_thread.app.activeWindow().windowTitle() == 'Duplicate Video')
    pyautogui.press('enter')

    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    new_total_count_expected = 1

    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.list_widget.count() == new_total_count_expected)
    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.thread_pool.activeThreadCount() == 0)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    frames_3_sec = int(round(29.97 * 3))

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.42, 0.43), current_frame_no=frames_3_sec),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_open_same_video_twice(app_thread, windows_container, blank_state):   
    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    video_path = get_test_vid_path()
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

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)
    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))
    app_thread.cmd.submit_cmd(Command(CommandType.ADD_ITEM_DND_WINDOW, [video_path.str()]))
    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)
    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    wait_until(lambda: app_thread.app.activeWindow().windowTitle() == 'Duplicate Video')
    pyautogui.press('enter')

    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    new_total_count_expected = 1

    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.list_widget.count() == new_total_count_expected)
    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.thread_pool.activeThreadCount() == 0)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

    # time.sleep(3)

