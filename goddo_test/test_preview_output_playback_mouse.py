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
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:01:05.00')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_after_in_frame_try_to_scroll_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:01:03.00')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_try_to_scroll_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:01:03.00')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    pyautogui.scroll(1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_in_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 65

    enter_time_in_go_to_dialog_box(app_thread, '0:01:05.00')

    # scroll back to in frame
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.18, 0.19), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_scroll_left_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 85

    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.43, 0.44), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_scroll_right_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 95

    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')

    # scroll back
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.56, 0.57), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_scroll_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:01:55.00')

    # scroll right
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_out_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 115

    enter_time_in_go_to_dialog_box(app_thread, '0:01:55.00')

    # scroll right
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.81, 0.82), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_try_to_scroll_right_from_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:01:55.00')

    # scroll right
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # scroll right
    pyautogui.scroll(-1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_from_before_out_frame_try_to_scroll_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:01:58.00')

    # scroll right
    go_to_prev_wind_slider(windows_container.output_window, 0.1)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_to_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_start_frame = 4 * 50
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # scroll to start frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_start_frame_try_to_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_start_frame = 4 * 50
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # scroll to start frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    # scroll left
    pyautogui.scroll(1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_after_start_frame_try_to_pass_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:52.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_start_frame = 4 * 50
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # scroll pass start frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_start_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_start_frame = 4 * 50
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 55

    # scroll to start frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.06, 0.07), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_start_and_in_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:52.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 57

    # scroll to start frame
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.08, 0.09), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_start_and_in_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:57.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 52

    # scroll to start frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.02, 0.03), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_right_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # scroll to in frame
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_in_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 65

    # scroll to in frame
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.18, 0.19), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_left_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # scroll to in frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_in_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 55

    # scroll to in frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.06, 0.07), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_right_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:58.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 63

    # scroll pass in frame
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.16, 0.17), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_left_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:02.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 57

    # scroll pass in frame
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.08, 0.09), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_in_and_out_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 95

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.56, 0.57), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_in_and_out_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 85

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.43, 0.44), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_right_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:55.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_out_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:55.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 125

    # scroll right to out frame
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.93, 0.94), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_left_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_out_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 115

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.81, 0.82), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_before_out_frame_scroll_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:58.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 123

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.91, 0.92), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_after_out_frame_scroll_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:02.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 117

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.83, 0.84), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_out_and_end_frame_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:02.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 127

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.96, 0.97), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_from_bet_out_and_end_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:07.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 122

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.89, 0.91), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_scroll_to_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_from_end_frame_try_to_scroll_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    # scroll right
    pyautogui.scroll(-1)
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_from_end_frame_scroll_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:05.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130
    expected_cur_frame = 4 * 125

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    # scroll left
    pyautogui.scroll(1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.93, 0.94), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_from_end_frame_try_to_scroll_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:08.00')

    go_to_prev_wind_slider(windows_container.output_window, 0.1)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130

    # scroll right
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

# def test_unrestricted_move_with_mouse_scroll(app_thread, windows_container: WindowsContainer, blank_state):
#     open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

#     pyautogui.press('f')
#     wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

#     expected_start_frame = 4 * 50
#     expected_in_frame = 4 * 60 * 1
#     expected_out_frame = 4 * 60 * 2
#     expected_end_frame = 4 * 130

#     enter_time_in_go_to_dialog_box(app_thread, '0:00:51.00')
#     go_to_prev_wind_slider(windows_container.output_window, 0.1)

#     # try to scroll pass start frame
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

#     # when exactly on start frame, try to scroll back
#     pyautogui.scroll(1)
#     time.sleep(0.5)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

#     # scroll forward when on start frame
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame + 4 * 5)

#     # scroll back and forth when between start and in frame
#     enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 55)

#     # scroll back and forth on in frame
#     enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame + 4*5)
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame - 4*5)

#     enter_time_in_go_to_dialog_box(app_thread, '0:01:02.00')
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame - 4*3)
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame + 4*2)

#     # # scroll backward when between in and out frame
#     enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 95)
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 90)

#     # scroll back and forth on out frame
#     enter_time_in_go_to_dialog_box(app_thread, '0:01:55.00')
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame + 4*5)
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame - 4*5)

#     enter_time_in_go_to_dialog_box(app_thread, '0:02:02.00')
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame - 4*3)
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame + 4*2)

#     # scroll back and forth when between out and end frame
#     enter_time_in_go_to_dialog_box(app_thread, '0:02:08.00')
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame + 4*3)
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame + 4*8)

#     # stops at end frame
#     pyautogui.scroll(-1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

#     # when exactly on out frame, try to scroll forward
#     pyautogui.scroll(-1)
#     time.sleep(0.5)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

#     # scroll backward when on out frame
#     pyautogui.scroll(1)
#     wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame - 4*5)

#     clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
#     expected_timeline_clips = [(clip,120)]

#     expected_cur_frame = expected_end_frame - 4*5

#     generic_assert(app_thread, windows_container, blank_state,
#                 get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
#                 get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
#                 get_assert_preview_fn(clip, slider_range=(0.93, 0.94), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
#                 get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_move_with_mouse_click(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no
    before_slider_value = app_thread.mon.preview_window_output.slider.value()

    expected_start_frame = 4 * 50
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130

    assert expected_in_frame <= before_frame_no <= expected_out_frame

    click_on_prev_wind_slider(windows_container.output_window, 0.1, should_slider_value_change=False)
    time.sleep(0.5)
    assert app_thread.mon.state.preview_window_output.current_frame_no == before_frame_no
    assert app_thread.mon.preview_window_output.slider.value() == before_slider_value

    click_on_prev_wind_slider(windows_container.output_window, 0.9, should_slider_value_change=False)
    time.sleep(0.5)
    assert app_thread.mon.state.preview_window_output.current_frame_no == before_frame_no
    assert app_thread.mon.preview_window_output.slider.value() == before_slider_value

    click_on_prev_wind_slider(windows_container.output_window, 0.5, should_slider_value_change=False)
    wait_until(lambda: expected_in_frame <= app_thread.mon.state.preview_window_output.current_frame_no <= expected_out_frame)
    assert 99 <= app_thread.mon.preview_window_output.slider.value() <= 101

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.45, 0.55), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

# unrestricted mouse click
#   click between start and in frame, should go there
#   click between in/out frame, should go there
#   click between out and end frame, should go there
#   try to drag mouse pass in frame
#   try to drag mouse pass start frame
#   try to drag mouse pass out frame
#   try to drag mouse pass end frame
def test_unrestricted_mouse_click_before_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no
    before_slider_value = app_thread.mon.preview_window_output.slider.value()

    expected_start_frame = 4 * 50
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130

    #   click between start and in frame
    click_on_prev_wind_slider(windows_container.output_window, 0.01)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.03), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_click_between_in_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no
    before_slider_value = app_thread.mon.preview_window_output.slider.value()

    expected_start_frame = 4 * 50
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130

    #   click between start and in frame
    click_on_prev_wind_slider(windows_container.output_window, 0.5)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.49, 0.51), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_click_after_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no
    before_slider_value = app_thread.mon.preview_window_output.slider.value()

    expected_start_frame = 4 * 50
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130

    #   click between start and in frame
    click_on_prev_wind_slider(windows_container.output_window, 0.99)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.97, 1), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_drag_left_within_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.7)
    x2_offset = int(slider.width() * 0.3)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    assert app_thread.mon.state.preview_window_output.current_frame_no <= 4 * 60 * 2
    assert app_thread.mon.preview_window_output.slider.value() <= 176

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.28, 0.32), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_drag_right_within_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.3)
    x2_offset = int(slider.width() * 0.7)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    assert app_thread.mon.state.preview_window_output.current_frame_no <= 4 * 60 * 2
    assert app_thread.mon.preview_window_output.slider.value() <= 176

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.68, 0.72), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_drag_left_pass_in(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.5)
    x2_offset = int(slider.width() * 0.05)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    assert app_thread.mon.state.preview_window_output.current_frame_no <= 4 * 60 * 2
    assert app_thread.mon.preview_window_output.slider.value() <= 176

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.15), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_mouse_drag_right_pass_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.5)
    x2_offset = int(slider.width() * 0.95)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    assert app_thread.mon.state.preview_window_output.current_frame_no <= 4 * 60 * 2
    assert app_thread.mon.preview_window_output.slider.value() <= 176

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.88), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_drag_right_within_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.3)
    x2_offset = int(slider.width() * 0.7)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    assert app_thread.mon.state.preview_window_output.current_frame_no <= 4 * 60 * 2
    assert app_thread.mon.preview_window_output.slider.value() <= 176

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.68, 0.72), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_mouse_drag_left_pass_in(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    slider = app_thread.mon.preview_window_output.slider
    pos = local_to_global_pos(slider, app_thread.mon.preview_window_output)
    x1_offset = int(slider.width() * 0.5)
    x2_offset = int(slider.width() * 0.05)
    y_offset = int(slider.height() * 0.5)
    drag_and_drop(pos.x() + x1_offset, pos.y() + y_offset, pos.x() + x2_offset, pos.y() + y_offset)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    assert app_thread.mon.state.preview_window_output.current_frame_no <= 4 * 60 * 2
    assert app_thread.mon.preview_window_output.slider.value() <= 176

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.15), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_video_stops_at_out_with_restrict_with_playing(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_blank_1hr_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:00.00')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)

    drop_cur_to_timeline(windows_container)

    timeline_window = windows_container.timeline_window
    pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    pyautogui.doubleClick(x=pt.x() + 50 + 10, y=pt.y() + 68 + 10)
    wait_until(lambda: windows_container.output_window.preview_widget.cap is not None)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:58.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(3)

    logging.info(f'=== out frame {app_thread.mon.state.preview_window_output.current_frame_no}')

    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))
