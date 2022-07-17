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

def test_restricted_keyboard_move_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:01.03')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_from_after_in_frame_try_to_move_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:00.03')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_try_to_move_to_before_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:01.03')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    #   try move to before in frame
    pyautogui.press('left')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_try_to_move_to_before_in_frame_then_move_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:01.03')

    expected_cur_frame = expected_in_frame + 1

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    #   try move to before in frame
    pyautogui.press('left')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    # move to in frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_move_right_from_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:01.03')

    expected_cur_frame = expected_in_frame + 1

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    # move to in frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_move_left_from_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    expected_cur_frame = frames_59_mins + 4 * 29 + 1

    #   from in frame move right
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.55, 0.56), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_move_right_from_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    expected_cur_frame = frames_59_mins + 4 * 30 + 3

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.57, 0.58), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_move_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '1:00:00.01')

    # move to out frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_try_to_move_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '1:00:00.01')

    # move to out frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.press('right')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_move_left_from_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '1:00:00.01')

    expected_cur_frame = expected_end_frame - 5

    # move to out frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_try_to_move_pass_out_frame_then_move_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '1:00:00.01')

    expected_cur_frame = expected_end_frame - 5

    # move to out frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.press('right')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_to_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:51.03')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_try_to_move_pass_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:50.03')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_try_to_move_pass_start_frame_then_move_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:50.03')

    expected_cur_frame = expected_start_frame + 1

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_from_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:51.03')

    expected_cur_frame = expected_start_frame + 1

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_bet_start_and_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    expected_cur_frame = frames_59_mins + 4 * 29 + 1

    #   from in frame move right
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.55, 0.56), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_bet_start_and_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    expected_cur_frame = frames_59_mins + 4 * 30 + 3

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.57, 0.58), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:00.01')

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_from_in_frame_move_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:01.03')

    expected_cur_frame = expected_in_frame + 1

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    # move to in frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:01.03')

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.14, 0.15), current_frame_no=expected_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_and_skip_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:00.03')

    expected_cur_frame = expected_in_frame - 4

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.13, 0.14), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_from_in_frame_move_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:01.03')

    expected_cur_frame = expected_in_frame - 5

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    # move left
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_from_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    expected_cur_frame = frames_59_mins + 4 * 29 + 1

    #   from in frame move right
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.55, 0.56), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_from_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    expected_cur_frame = frames_59_mins + 4 * 30 + 3

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.57, 0.58), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '1:00:00.01')

    # move to out frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_from_out_frame_move_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '1:00:00.01')

    expected_cur_frame = expected_end_frame - 5

    # move to out frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

