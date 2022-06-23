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

def test_slider_disabled_initially(windows_container: WindowsContainer):
    assert not windows_container.output_window.slider.isEnabled()

    click_on_prev_wind_slider(windows_container.output_window, 0.9, should_slider_value_change=False)

    assert windows_container.output_window.preview_widget.frame_pixmap is None
    assert windows_container.output_window.slider.value() == 0

def test_restricted_video_plays_on_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > expected_in_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.15), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_video_plays_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > expected_in_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.50, 0.53), is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_video_plays_and_stops_on_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:59.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(2)

    logging.info(f'=== out frame {app_thread.mon.state.preview_window_output.current_frame_no}')

    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_on_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:50.00')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.03), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_bet_start_and_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.06, 0.09), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_pass_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:59.00')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(2)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.15), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_on_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.15), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > expected_in_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.50, 0.53), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_pass_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:59.00')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(2)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.9), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_on_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:00.00')

    before_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > before_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.9), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_bet_out_and_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:05.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_play(windows_container.output_window)
    time.sleep(1)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no > expected_out_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.94, 0.96), is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_video_plays_till_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:09.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_end_frame = 4 * 130

    press_space_to_play(windows_container.output_window)
    time.sleep(2)
    press_space_to_pause(windows_container.output_window)

    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_end_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_end_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_in_frame_front_restricted_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:10.00')

    expected_new_in_frame = 4 * 70 * 1
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 70 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.in_frame == expected_new_in_frame
    

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_new_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(output_clip,100)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(prev_clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(output_clip, slider_range=(0.14, 0.15), current_frame_no=expected_new_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_in_frame_front_unrestricted_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:10.00')

    expected_new_in_frame = 4 * 70 * 1
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 70 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.in_frame == expected_new_in_frame
    

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_new_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(output_clip,100)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(prev_clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(output_clip, slider_range=(0.14, 0.15), current_frame_no=expected_new_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_in_frame_back_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00')

    expected_new_in_frame = 4 * 55 * 1
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 85 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.in_frame == expected_new_in_frame

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_new_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(output_clip,130)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(prev_clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(output_clip, slider_range=(0.11, 0.12), current_frame_no=expected_new_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_in_frame_back_to_start_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:50.00')

    expected_new_in_frame = 4 * 50 * 1
    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 90 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.in_frame == expected_new_in_frame

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_new_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(output_clip,140)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(prev_clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(output_clip, slider_range=(0.11, 0.12), current_frame_no=expected_new_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_out_frame_back_restricted_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:50.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_new_out_frame = 4 * 110

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 70 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame
    

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,100)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(prev_clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(output_clip, slider_range=(0.85, 0.86), current_frame_no=expected_new_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_out_frame_back_unrestricted_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:50.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_new_out_frame = 4 * 110

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 70 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame
    

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,100)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(prev_clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(output_clip, slider_range=(0.85, 0.86), current_frame_no=expected_new_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))


def test_move_out_frame_front_restricted_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:05.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_new_out_frame = 4 * 125

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 85 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame
    

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,130)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(prev_clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(output_clip, slider_range=(0.88, 0.89), current_frame_no=expected_new_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_move_out_frame_front_to_end_in_clip(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    enter_time_in_go_to_dialog_box(app_thread, '0:02:10.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_new_out_frame = 4 * 130

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window_output.cur_total_frames == 4 * 90 + 1)
    assert app_thread.mon.state.timeline.clips[0].frame_in_out.out_frame == expected_new_out_frame
    

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    output_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_new_out_frame)
    expected_timeline_clips = [(output_clip,140)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(prev_clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(output_clip, slider_range=(0.88, 0.89), current_frame_no=expected_new_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_not_enough_extra_frames_on_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:00:05.00', '0:01:05.00', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')

    expected_in_frame = 4 * 5
    expected_out_frame = 4 * 65    

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(prev_clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(prev_clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(prev_clip, slider_range=(0.06, 0.07), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=19, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_no_extra_frames_on_left(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:00:00.01', '0:01:00.01', get_blank_1hr_vid_path())

    enter_time_in_go_to_dialog_box(app_thread, '0:00:00.01')

    expected_in_frame = 1
    expected_out_frame = 4 * 60 + 1  

    prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(prev_clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(prev_clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(prev_clip, slider_range=(0.00, 0.01), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

# def test_not_enough_extra_frames_on_right(app_thread, windows_container: WindowsContainer, blank_state):
#     open_clip_on_output_window(app_thread, windows_container, '0:58:55.00', '0:59:55.00', get_blank_1hr_vid_path())

#     enter_time_in_go_to_dialog_box(app_thread, '0:58:55.00')

#     expected_in_frame = 4 * (58 * 60 + 55)
#     expected_out_frame = 4 * (59 * 60 + 55)

#     prev_clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
#     expected_timeline_clips = [(prev_clip,120)]

#     generic_assert(app_thread, windows_container, blank_state,
#                 get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
#                 get_assert_preview_fn(prev_clip, slider_range=(0.99, 1), current_frame_no=expected_out_frame),
#                 get_assert_preview_fn(prev_clip, slider_range=(0.93, 0.94), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=22), 
#                 get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))
