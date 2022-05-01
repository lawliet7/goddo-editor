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
from goddo_test.utils.assert_utils import *
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.test_utils import click_on_prev_wind_slider, drag_and_drop, drop_video_on_preview, get_blank_15m_vid_path, get_current_method_name, get_img_asset, get_test_vid_path, grab_screenshot, save_reload_and_assert_state, wait_until, pil_img_to_arr, cmp_image
from goddo_test.utils.windows_container import WindowsContainer


def test_drop_clip_in_only(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(in_frame=in_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame))

def test_drop_clip_in_only_hover(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    hover_over_rect_and_assert(windows_container.timeline_window)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(in_frame=in_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame))

def test_drop_clip_out_only(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    click_on_prev_wind_slider(windows_container.preview_window, 0.95)

    pyautogui.press('o')

    out_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(slider_range=(0.93,0.97),out_frame=out_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(out_frame=out_frame))

def test_drop_clip_out_only_hover(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    click_on_prev_wind_slider(windows_container.preview_window, 0.95)

    pyautogui.press('o')

    out_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    hover_over_rect_and_assert(windows_container.timeline_window)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(slider_range=(0.93,0.97),out_frame=out_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(out_frame=out_frame))            

def test_drop_clip_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    click_on_prev_wind_slider(windows_container.preview_window, 0.95)

    pyautogui.press('o')

    out_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(slider_range=(0.93,0.97), in_frame=in_frame, out_frame=out_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame, out_frame=out_frame))

def test_drop_clip_in_out_hover(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    click_on_prev_wind_slider(windows_container.preview_window, 0.95)

    pyautogui.press('o')

    out_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    hover_over_rect_and_assert(windows_container.timeline_window)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(slider_range=(0.93,0.97), in_frame=in_frame, out_frame=out_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame, out_frame=out_frame))            

def test_zoom_in_on_timeline(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    for _ in range(3):
        pyautogui.press('add')

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(in_frame=in_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame, width_of_one_min=138))

def test_zoom_out_on_timeline(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    for _ in range(3):
        pyautogui.press('subtract')

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(in_frame=in_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame, width_of_one_min=102))

def test_timeline_width_expand(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_blank_15m_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')
    in_frame = app_thread.mon.state.preview_window.current_frame_no

    click_on_prev_wind_slider(windows_container.preview_window, 0.333)

    pyautogui.press('o')
    out_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)
    drop_cur_to_timeline(windows_container)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_15m_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_15m_file_fn(slider_range=(0.32,0.34), in_frame=in_frame, out_frame=out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            get_assert_timeline_for_15m_file_fn(in_frame=in_frame, out_frame=out_frame, num_of_clips=2))
    

def hover_over_rect_and_assert(timeline_window, idx: int = 0, assert_threshold: int = 0.9):
    _, rect = timeline_window.inner_widget.clip_rects[idx]
    corner_pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    x = int(corner_pt.x() + rect.x() + rect.width() / 2)
    y = int(corner_pt.y() + rect.y() + rect.height() / 2)

    pyautogui.moveTo(int(corner_pt.x() + rect.x() + rect.width() / 2), int(corner_pt.y() + rect.y() + rect.height() / 2))
    time.sleep(1)

    template_img = get_img_asset('hover_template.png')
    screen_img = grab_screenshot((x, y, 100, 100))

    assert cmp_image(screen_img, template_img) >= assert_threshold

def drop_cur_to_timeline(windows_container):
    preview_window = windows_container.preview_window
    src_corner_pt1 = local_to_global_pos(preview_window.preview_widget, preview_window)
    src_pt_x = int(src_corner_pt1.x() + preview_window.width() / 2)
    src_pt_y = int(src_corner_pt1.y() + preview_window.height() / 2)

    timeline_window = windows_container.timeline_window
    dest_corner_pt2 = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    dest_pt_x = int(dest_corner_pt2.x() + timeline_window.width() / 2)
    dest_pt_y = int(dest_corner_pt2.y() + timeline_window.height() / 2)

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    wait_until(lambda: len(timeline_window.inner_widget.clip_rects) > 0)
