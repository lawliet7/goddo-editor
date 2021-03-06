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

def test_restricted_video_plays_on_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:00.02')

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > expected_in_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.15, 0.17), is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_video_plays_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > expected_in_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_fn(clip, slider_range=(0.58, 0.59), is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_video_plays_and_stops_on_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:59.02')

    press_space_to_play(windows_container.output_window)
    time.sleep(2)

    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(clip, slider_range=(0.99, 1), is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_on_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:50.02')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(clip, slider_range=(0.01, 0.03), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0),
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_bet_start_and_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:52.02')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(clip, slider_range=(0.04, 0.07), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0),
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:59.02')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    press_space_to_play(windows_container.output_window)
    time.sleep(2)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
        get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False),
        get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
        get_assert_preview_fn(clip, slider_range=(0.15, 0.17), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0),
        get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_on_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:00.02')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
        get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False),
        get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
        get_assert_preview_fn(clip, slider_range=(0.15, 0.17), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0),
        get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:30.02')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
        get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False),
        get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
        get_assert_preview_fn(clip, slider_range=(0.58, 0.59), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0),
        get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_till_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:59.02')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    press_space_to_play(windows_container.output_window)
    time.sleep(2)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
        get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False),
        get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
        get_assert_preview_fn(clip, slider_range=(0.99, 1), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0),
        get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_in_frame_front_restricted_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:10.02')

    expected_new_in_frame = expected_in_frame + 4 * 10

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 60 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.in_frame == expected_new_in_frame

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_new_in_frame, out_frame=None)
    expected_timeline_clips = [(output_clip,100)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.16, 0.17), current_frame_no=expected_new_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=0), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_in_frame_front_unrestricted_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:10.02')

    expected_new_in_frame = expected_in_frame + 4 * 10

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 60 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.in_frame == expected_new_in_frame

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_new_in_frame, out_frame=None)
    expected_timeline_clips = [(output_clip,100)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.16, 0.17), current_frame_no=expected_new_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_in_frame_back_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:55.02')

    expected_new_in_frame = expected_in_frame - 4 * 5

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 75 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.in_frame == expected_new_in_frame

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_new_in_frame, out_frame=None)
    expected_timeline_clips = [(output_clip,130)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.13, 0.14), current_frame_no=expected_new_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_in_frame_back_to_start_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:58:50.02')

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 80 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.in_frame == expected_start_frame

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_start_frame, out_frame=None)
    expected_timeline_clips = [(output_clip,140)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.12, 0.13), current_frame_no=expected_start_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=0), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_move_out_frame_back_less_than_10_secs(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:55.02')

    expected_new_out_frame = expected_end_frame - 4 * 5

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame)
    

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,110)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.92, 0.93), current_frame_no=expected_new_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=20), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_move_out_frame_back_more_than_10_secs(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:45.02')

    expected_new_out_frame = expected_end_frame - 4 * 15

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 65 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,90)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.84, 0.85), current_frame_no=expected_new_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_move_out_frame_back_10_secs(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:50.02')

    expected_new_out_frame = expected_end_frame - 4 * 10

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame)

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,100)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.85, 0.86), current_frame_no=expected_new_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_move_out_frame_back_more_than_10_secs_in_2_takes(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:54.02')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_end_frame - 4 * 6)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:49.02')

    expected_new_out_frame = expected_end_frame - 4 * 11

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 69 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,98)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.85, 0.86), current_frame_no=expected_new_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

# -------------

def test_unrestricted_move_out_frame_back_less_than_10_secs(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:55.02')

    expected_new_out_frame = expected_end_frame - 4 * 5

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame)
    

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,110)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.92, 0.93), current_frame_no=expected_new_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=20), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_move_out_frame_back_more_than_10_secs(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:45.02')

    expected_new_out_frame = expected_end_frame - 4 * 15

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 65 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,90)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.84, 0.85), current_frame_no=expected_new_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_move_out_frame_back_10_secs(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:50.02')

    expected_new_out_frame = expected_end_frame - 4 * 10

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame)

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,100)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.85, 0.86), current_frame_no=expected_new_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_move_out_frame_back_more_than_10_secs_in_2_takes(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:54.02')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_end_frame - 4 * 6)

    enter_time_in_go_to_dialog_box(app_thread, '0:59:49.02')

    expected_new_out_frame = expected_end_frame - 4 * 11

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 69 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,98)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_fn(prev_clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
            get_assert_preview_fn(output_clip, slider_range=(0.85, 0.86), current_frame_no=expected_new_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_delete_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:59:00.02', None, get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:59:00.02')

    timeline_window = windows_container.timeline_window
    pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    pyautogui.click(x=pt.x() + 10 + 10, y=pt.y() + 68 + 10)
    pyautogui.press('delete')
    wait_until(lambda: len(windows_container.timeline_window.inner_widget.clip_rects) == 0)
    wait_until(lambda: windows_container.output_window.preview_widget.cap is None)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=None)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.98, 0.99), current_frame_no=expected_in_frame),
                get_assert_preview_for_blank_file_fn(is_output_window=True),
                assert_blank_timeline)
