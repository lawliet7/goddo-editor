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

def test_restricted_keyboard_move_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.01')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_from_after_in_frame_try_to_move_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.03')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_try_to_move_to_before_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.01')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # move to in frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    #   try move to before in frame
    pyautogui.press('left')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_try_to_move_to_before_in_frame_then_move_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.01')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = expected_in_frame + 1

    # move to in frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    #   try move to before in frame
    pyautogui.press('left')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    # move to in frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.125, 0.135), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_move_right_from_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.01')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = expected_in_frame + 1

    # move to in frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    #   from in frame move right
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no ==expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.13, 0.14), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_move_left_from_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 90 - 5

    #   from in frame move right
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.48, 0.49), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_move_right_from_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 90 + 1

    #   from in frame move right
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.49, 0.51), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_move_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:59.03')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # move to out frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_try_to_move_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:02:00.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # move to out frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # try to move pass out frame
    pyautogui.press('right')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_move_left_from_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:02:00.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = expected_out_frame - 5

    # move to out frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # move back from out frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.86), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_keyboard_try_to_move_pass_out_frame_then_move_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:02:00.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = expected_out_frame - 5

    # move to out frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # try to move pass out frame
    pyautogui.press('right')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # move back from out frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.86), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_to_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 50

    enter_time_in_go_to_dialog_box(app_thread, '0:00:50.01')

    #   move to start frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_try_to_move_pass_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 50

    enter_time_in_go_to_dialog_box(app_thread, '0:00:50.01')
    
    #   move to start frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    pyautogui.press('left')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_try_to_move_pass_start_frame_then_move_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_start_frame = 4 * 50
    expected_cur_frame = expected_start_frame + 1

    enter_time_in_go_to_dialog_box(app_thread, '0:00:50.01')
    
    #   move to start frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 50)

    pyautogui.press('left')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 50)

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_from_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_start_frame = 4 * 50
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = expected_start_frame + 1

    enter_time_in_go_to_dialog_box(app_thread, '0:00:50.01')
    
    #   move to start frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_start_frame)

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_bet_start_and_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 55 - 5

    #   move to between start and in frame, 
    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.04, 0.05), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_bet_start_and_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 55 + 1

    #   move to between start and in frame, 
    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.06, 0.07), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:00:59.03')

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_from_in_frame_move_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = expected_in_frame + 1

    enter_time_in_go_to_dialog_box(app_thread, '0:00:59.03')

    # move to in frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    # move right
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:01:01.01')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_and_skip_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 59 + 2

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.03')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.11, 0.12), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_from_in_frame_move_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = expected_in_frame - 5

    enter_time_in_go_to_dialog_box(app_thread, '0:01:01.01')

    # move to in frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    # move left
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.105, 0.115), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_from_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 90 - 5

    #   from in frame move right
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.48, 0.49), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_from_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 90 + 1

    #   from in frame move right
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.49, 0.51), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:01:59.03')

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_from_out_frame_move_right(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = expected_out_frame + 1

    enter_time_in_go_to_dialog_box(app_thread, '0:01:59.03')

    # move to in frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # move right
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    enter_time_in_go_to_dialog_box(app_thread, '0:02:01.01')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_and_skip_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 119 + 2

    enter_time_in_go_to_dialog_box(app_thread, '0:02:00.03')

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.86, 0.87), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_from_out_frame_move_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = expected_out_frame - 5

    enter_time_in_go_to_dialog_box(app_thread, '0:02:01.01')

    # move to in frame
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    # move left
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.86), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_left_from_bet_out_and_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:05.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 125 - 5

    #   from in frame move right
    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.92, 0.93), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_right_from_bet_out_and_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:05.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 125 + 1

    #   from in frame move right
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.935, 0.945), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_move_to_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:09.03')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130

    # move to end frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_try_to_move_pass_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:09.03')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130

    # move to end frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.press('right')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_keyboard_try_to_move_pass_end_frame_then_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:09.03')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130
    expected_cur_frame = expected_end_frame - 5

    # move to end frame
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.press('right')
    time.sleep(0.5)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    pyautogui.press('left')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

