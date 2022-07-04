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
from goddo_player.utils.window_util import get_center_pos_of_widget, local_to_global_pos
from goddo_test.common_asserts import assert_state_is_blank
from goddo_test.utils.assert_utils import *
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.test_utils import *
from goddo_test.utils.windows_container import WindowsContainer

def test_restricted_mouse_scroll_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60
    expected_cur_frame = 1

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_after_in_frame_try_to_scroll_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60
    expected_cur_frame = 1

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_try_to_scroll_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60
    expected_cur_frame = 1

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    pyautogui.scroll(1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_in_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 1
    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 5 + 1

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')

    # scroll back to in frame
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.07, 0.08), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_scroll_left_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 25

    enter_time_in_go_to_dialog_box(app_thread, '0:00:30.00')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.35, 0.36), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_scroll_right_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 35

    enter_time_in_go_to_dialog_box(app_thread, '0:00:30.00')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.495, 0.505), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_scroll_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    # scroll right
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.86), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_out_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 55

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    # scroll right
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.78, 0.79), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_try_to_scroll_right_from_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    # scroll right
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # scroll right
    pyautogui.scroll(-1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.86), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_before_out_frame_try_to_scroll_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60

    enter_time_in_go_to_dialog_box(app_thread, '0:00:58.00')

    # scroll right
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.86), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_to_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_start_frame = 1
    expected_out_frame = 4 * 60

    # scroll to start frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_start_frame_try_to_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_start_frame = 1
    expected_out_frame = 4 * 60

    # scroll to start frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    # scroll left
    pyautogui.scroll(1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_after_start_frame_try_to_pass_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:02.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_start_frame = 1
    expected_out_frame = 4 * 60

    # scroll pass start frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_start_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_start_frame = 1
    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 5 + expected_start_frame

    # scroll to start frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.07, 0.08), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_in_and_out_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:30.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 35

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.495, 0.505), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_in_and_out_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:30.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 25

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.35, 0.36), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_right_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.86), current_frame_no=expected_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_out_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 65

    # scroll right to out frame
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.92, 0.93), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_left_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.86), current_frame_no=expected_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_out_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 55

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.78, 0.79), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_before_out_frame_scroll_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:58.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 63

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.895, 0.905), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_after_out_frame_scroll_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:02.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 57

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.81, 0.82), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_out_and_end_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:02.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 67

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.95, 0.96), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_out_and_end_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:07.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 62

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.88, 0.89), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_to_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_end_frame = 4 * 70

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_from_end_frame_try_to_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_end_frame = 4 * 70

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    # scroll right
    pyautogui.scroll(-1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_from_end_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_end_frame = 4 * 70
    expected_cur_frame = 4 * 65

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.92, 0.93), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_from_end_frame_try_to_scroll_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:08.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_out_frame = 4 * 60
    expected_end_frame = 4 * 70

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_click_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no
    before_slider_value = app_thread.mon.preview_window_output.slider.value()

    expected_out_frame = 4 * 60

    click_on_prev_wind_slider(windows_container.output_window, 0.5, should_slider_value_change=False)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no)
    wait_until(lambda: app_thread.mon.preview_window_output.slider.value() > before_slider_value)

    logging.info(f'=== before slider {before_slider_value} after slider {app_thread.mon.preview_window_output.slider.value() }')

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.49, 0.51), is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_click_after_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no
    before_slider_value = app_thread.mon.preview_window_output.slider.value()

    expected_out_frame = 4 * 60

    click_on_prev_wind_slider(windows_container.output_window, 0.95, should_slider_value_change=False)

    time.sleep(0.5)
    assert app_thread.mon.state.preview_window_output.current_frame_no == before_frame_no
    assert app_thread.mon.preview_window_output.slider.value() == before_slider_value

    logging.info(f'=== before slider {before_slider_value} after slider {app_thread.mon.preview_window_output.slider.value() }')

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    slider_range_tuple = (before_slider_value/200-0.01, before_slider_value/200+0.01)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=slider_range_tuple, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_click_between_in_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_out_frame = 4 * 60

    #   click between start and in frame
    click_on_prev_wind_slider(windows_container.output_window, 0.5)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.49, 0.51), is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_click_after_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_out_frame = 4 * 60

    #   click between start and in frame
    click_on_prev_wind_slider(windows_container.output_window, 0.99)

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.97, 1), is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_drag_left_within_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.7)
    x2_offset = int(slider.width() * 0.3)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    expected_out_frame = 4 * 60

    assert app_thread.mon.state.preview_window_output.current_frame_no <= expected_out_frame
    assert app_thread.mon.preview_window_output.slider.value() <= 172

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.28, 0.32), is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_drag_right_within_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.3)
    x2_offset = int(slider.width() * 0.7)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    expected_out_frame = 4 * 60

    assert app_thread.mon.state.preview_window_output.current_frame_no <= expected_out_frame
    assert app_thread.mon.preview_window_output.slider.value() <= 172

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.68, 0.72), is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_drag_right_pass_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.5)
    x2_offset = int(slider.width() * 0.95)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    expected_out_frame = 4 * 60

    assert app_thread.mon.state.preview_window_output.current_frame_no <= expected_out_frame
    assert app_thread.mon.preview_window_output.slider.value() <= 172

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.88), is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_drag_right_within_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.3)
    x2_offset = int(slider.width() * 0.7)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    expected_out_frame = 4 * 60

    assert app_thread.mon.state.preview_window_output.current_frame_no <= expected_out_frame
    assert app_thread.mon.preview_window_output.slider.value() <= 172

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.68, 0.72), is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))
