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

def test_restricted_go_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60
    expected_cur_frame = 1

    # go to in frame
    enter_time_in_go_to_dialog_box(app_thread, '0:00:00.01')
    assert windows_container.output_window.slider.value() == 0
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame    

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_go_to_bet_in_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 30

    # go to between in and out frame
    enter_time_in_go_to_dialog_box(app_thread, '0:00:30.00')
    assert 84 <= windows_container.output_window.slider.value() <= 86
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.42, 0.43), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_go_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    expected_out_frame = 4 * 60

    # go to out frame
    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')
    assert 170 <= windows_container.output_window.slider.value() <= 172
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.86), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_go_to_neg_testcases(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    time_edit = windows_container.output_window.dialog.time_edit
    before_slider_value = windows_container.output_window.slider.value()
    before_cur_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    # go to between out and end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:01:05.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    # go to end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:01:10.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    # go to after end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:01:30.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 30

    enter_time_in_go_to_dialog_box(app_thread,'0:00:30.00')

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.42, 0.43), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_out_frame = 4 * 60
    expected_cur_frame = 1

    # go to in frame
    enter_time_in_go_to_dialog_box(app_thread, '0:00:00.01')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert windows_container.output_window.slider.value() == 0
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame    

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 30

    # go to between in and out frame
    enter_time_in_go_to_dialog_box(app_thread, '0:00:30.00')
    assert 84 <= windows_container.output_window.slider.value() <= 86
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.42, 0.43), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_out_frame = 4 * 60

    # go to out frame
    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert 170 <= windows_container.output_window.slider.value() <= 172
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.85, 0.86), current_frame_no=expected_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_bet_out_and_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 66

    # go to between out and end frame
    enter_time_in_go_to_dialog_box(app_thread, '0:01:06.00')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert 187 <= windows_container.output_window.slider.value() <= 189
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.93, 0.95), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 70

    # go to between out and end frame
    enter_time_in_go_to_dialog_box(app_thread, '0:01:10.00')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert 199 <= windows_container.output_window.slider.value() <= 200
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_neg_testcases(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, None, '0:01:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit
    before_slider_value = windows_container.output_window.slider.value()
    before_cur_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    # go to after end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:01:30.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    enter_time_in_go_to_dialog_box(app_thread,'0:00:30.00')

    expected_out_frame = 4 * 60
    expected_cur_frame = 4 * 30

    clip = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.01, 0.02), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.42, 0.43), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=0, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))
