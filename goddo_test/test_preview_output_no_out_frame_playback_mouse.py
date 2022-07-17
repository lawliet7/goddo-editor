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

frames_59_mins = 4 * 59 * 60
expected_in_frame = frames_59_mins + 2
expected_start_frame = 4 * 58 * 60 + 4 * 50 + 2
expected_end_frame = 4 * 60 * 60 + 2

def test_restricted_mouse_scroll_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:05.02')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_after_in_frame_try_to_scroll_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:02.02')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_in_frame_try_to_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:02.02')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    pyautogui.scroll(1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_in_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:02.02')

    expected_cur_frame = expected_in_frame + 4 * 5

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.21, 0.22), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_scroll_left_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    expected_cur_frame = expected_in_frame + 4 * 25

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.495, 0.505), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_scroll_right_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    expected_cur_frame = expected_in_frame + 4 * 35

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.64, 0.65), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_scroll_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:55.02')

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_out_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    expected_cur_frame = expected_end_frame - 4 * 5

    enter_time_in_go_to_dialog_box(app_thread, '0:59:55.02')

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.92, 0.93), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_try_to_scroll_right_from_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:55.02')

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.scroll(-1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_before_out_frame_try_to_scroll_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:58.02')

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_to_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:55.02')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_start_frame_try_to_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:55.02')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    pyautogui.scroll(1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_after_start_frame_try_to_pass_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:52.02')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_start_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:55.02')

    expected_cur_frame = expected_start_frame + 4 * 5

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    # scroll forward
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.07, 0.08), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_start_and_in_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:52.02')

    expected_cur_frame = expected_start_frame + 4 * 7

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.095, 0.105), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_start_and_in_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:57.02')

    expected_cur_frame = expected_start_frame + 4 * 2

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.02, 0.03), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_right_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:55.02')

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_in_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:55.02')

    expected_cur_frame = expected_in_frame + 4 * 5

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.21, 0.22), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_left_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:05.02')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_in_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:05.02')

    expected_cur_frame = expected_in_frame - 4 * 5

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.07, 0.08), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_right_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:58.02')

    expected_cur_frame = expected_in_frame + 4 * 3

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.18, 0.19), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_left_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:02.02')

    expected_cur_frame = expected_in_frame - 4 * 3

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.095, 0.105), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_in_and_out_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_cur_frame = expected_in_frame + 4 * 25

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.495, 0.505), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_in_and_out_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_cur_frame = expected_in_frame + 4 * 35

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.64, 0.65), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_to_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:55.02')

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_from_end_frame_try_to_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:55.02')

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.scroll(-1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_from_end_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:55.02')

    expected_cur_frame = expected_end_frame - 4 * 5

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.92, 0.93), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_from_end_frame_try_to_scroll_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:58.02')

    # scroll forward
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_click_before_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no
    before_slider_value = app_thread.mon.preview_window_output.slider.value()

    click_on_prev_wind_slider(windows_container.output_window, 0.05, should_slider_value_change=False)

    time.sleep(0.5)
    assert app_thread.mon.state.preview_window_output.current_frame_no == before_frame_no
    assert app_thread.mon.preview_window_output.slider.value() == before_slider_value

    logging.info(f'=== before slider {before_slider_value} after slider {app_thread.mon.preview_window_output.slider.value() }')

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    slider_range_tuple = (before_slider_value/200-0.01, before_slider_value/200+0.01)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=slider_range_tuple, current_frame_no=before_frame_no, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_click_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no
    before_slider_value = app_thread.mon.preview_window_output.slider.value()

    click_on_prev_wind_slider(windows_container.output_window, 0.5, should_slider_value_change=False)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no)
    wait_until(lambda: app_thread.mon.preview_window_output.slider.value() > before_slider_value)

    logging.info(f'=== before slider {before_slider_value} after slider {app_thread.mon.preview_window_output.slider.value() }')

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.45, 0.55), is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_click_before_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    #   click between start and in frame
    click_on_prev_wind_slider(windows_container.output_window, 0.01)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]
    
    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.03), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_click_between_in_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no
    before_slider_value = app_thread.mon.preview_window_output.slider.value()

    click_on_prev_wind_slider(windows_container.output_window, 0.5, should_slider_value_change=False)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no)
    wait_until(lambda: app_thread.mon.preview_window_output.slider.value() > before_slider_value)

    logging.info(f'=== before slider {before_slider_value} after slider {app_thread.mon.preview_window_output.slider.value() }')

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.45, 0.55), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_drag_left_within_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pw_state = app_thread.mon.state.preview_window_output

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.7)
    x2_offset = int(slider.width() * 0.3)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    floor = (0.28 * pw_state.cur_total_frames + pw_state.cur_start_frame)
    ceil = (0.32 * pw_state.cur_total_frames + pw_state.cur_start_frame)
    wait_until(lambda: floor < pw_state.current_frame_no < ceil)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.28, 0.32), is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_drag_right_within_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pw_state = app_thread.mon.state.preview_window_output

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.3)
    x2_offset = int(slider.width() * 0.7)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    floor = (0.68 * pw_state.cur_total_frames + pw_state.cur_start_frame)
    ceil = (0.72 * pw_state.cur_total_frames + pw_state.cur_start_frame)
    wait_until(lambda: floor < pw_state.current_frame_no < ceil)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.68, 0.72), is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_drag_left_pass_in(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pw_state = app_thread.mon.state.preview_window_output

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.5)
    x2_offset = int(slider.width() * 0.05)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    floor = (0.14 * pw_state.cur_total_frames + pw_state.cur_start_frame)
    ceil = (0.17 * pw_state.cur_total_frames + pw_state.cur_start_frame)
    wait_until(lambda: floor < pw_state.current_frame_no < ceil, error_msg_func=lambda: f'{floor} < {pw_state.current_frame_no} < {ceil}')

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.17), is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_drag_right_within_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pw_state = app_thread.mon.state.preview_window_output

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.5)
    x2_offset = int(slider.width() * 0.95)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    floor = (0.94 * pw_state.cur_total_frames + pw_state.cur_start_frame)
    ceil = (0.97 * pw_state.cur_total_frames + pw_state.cur_start_frame)
    wait_until(lambda: floor < pw_state.current_frame_no < ceil, error_msg_func=lambda: f'{floor} < {pw_state.current_frame_no} < {ceil}')

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.93, 0.97), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_drag_left_pass_in(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pw_state = app_thread.mon.state.preview_window_output

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.3)
    x2_offset = int(slider.width() * 0.05)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    floor = int(0.04 * pw_state.cur_total_frames + pw_state.cur_start_frame)
    ceil = int(round(0.06 * pw_state.cur_total_frames + pw_state.cur_start_frame))
    wait_until(lambda: floor <= pw_state.current_frame_no <= ceil, error_msg_func=lambda: f'{floor} <= {pw_state.current_frame_no} <= {ceil}')

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.04, 0.06), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))
