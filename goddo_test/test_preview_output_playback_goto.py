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
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    # go to in frame
    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')
    assert 24 <= windows_container.output_window.slider.value() <= 25
    assert app_thread.mon.state.preview_window_output.current_frame_no == 4 * 60

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_go_to_bet_in_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    # go to between in and out frame
    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')
    assert 99 <= windows_container.output_window.slider.value() <= 100
    assert app_thread.mon.state.preview_window_output.current_frame_no == 4 * 90

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 90

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.49, 0.51), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_go_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    # go to out frame
    enter_time_in_go_to_dialog_box(app_thread, '0:02:00.00')
    assert 174 <= windows_container.output_window.slider.value() <= 175
    assert app_thread.mon.state.preview_window_output.current_frame_no == 4 * 120

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_go_to_try_move_to_before_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    time_edit = windows_container.output_window.dialog.time_edit
    before_slider_value = windows_container.output_window.slider.value()
    before_cur_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    # go to before start frame
    enter_time_in_go_to_dialog_box(app_thread,'0:00:30.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    # go to start frame
    enter_time_in_go_to_dialog_box(app_thread, '0:00:50.00', False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    # go to between start frame and in frame
    enter_time_in_go_to_dialog_box(app_thread, '0:00:55.00', False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    # go to between out and end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:02:05.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    # go to end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:02:10.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    # go to after end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:02:30.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    enter_time_in_go_to_dialog_box(app_thread,'0:01:30.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 90

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.49, 0.51), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_restricted_go_to_try_move_to_after_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    time_edit = windows_container.output_window.dialog.time_edit
    before_slider_value = windows_container.output_window.slider.value()
    before_cur_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    # go to between out and end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:02:05.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    # go to end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:02:10.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    # go to after end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:02:30.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    enter_time_in_go_to_dialog_box(app_thread,'0:01:30.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 90

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.49, 0.51), current_frame_no=expected_cur_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_start_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 50

    # go to start frame
    enter_time_in_go_to_dialog_box(app_thread, '0:00:50.00')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert windows_container.output_window.slider.value() == 0
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0, 0.01), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_bet_start_and_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 54

    # go to between start frame and in frame
    enter_time_in_go_to_dialog_box(app_thread, '0:00:54.00')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert 9 <= windows_container.output_window.slider.value() <= 10
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.04, 0.06), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # go to in frame
    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert 24 <= windows_container.output_window.slider.value() <= 25
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_bet_in_and_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 90

    # go to between in and out frame
    enter_time_in_go_to_dialog_box(app_thread, '0:01:30.00')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert 99 <= windows_container.output_window.slider.value() <= 100
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.49, 0.51), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    # go to out frame
    enter_time_in_go_to_dialog_box(app_thread, '0:02:00.00')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert 174 <= windows_container.output_window.slider.value() <= 175
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_out_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_bet_out_and_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 126

    # go to between out and end frame
    enter_time_in_go_to_dialog_box(app_thread, '0:02:06.00')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert 189 <= windows_container.output_window.slider.value() <= 190
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.94, 0.96), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_end_frame(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 130

    # go to end frame
    enter_time_in_go_to_dialog_box(app_thread, '0:02:10.00')
    assert time_edit.styleSheet() == 'background-color: white;'
    assert 199 <= windows_container.output_window.slider.value() <= 200
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.99, 1), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_unrestricted_go_to_neg_testcases(app_thread, windows_container: WindowsContainer, blank_state):
    open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    pyautogui.press('f')
    wait_until(lambda: not app_thread.mon.state.preview_window_output.restrict_frame_interval)

    time_edit = windows_container.output_window.dialog.time_edit
    before_slider_value = windows_container.output_window.slider.value()
    before_cur_frame_no = app_thread.mon.state.preview_window_output.current_frame_no

    # go to before start frame
    enter_time_in_go_to_dialog_box(app_thread,'0:00:30.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    # go to after end frame
    enter_time_in_go_to_dialog_box(app_thread,'0:02:30.00',False)
    pyautogui.press('enter')
    time.sleep(0.5)
    assert not windows_container.output_window.dialog.isHidden()
    assert time_edit.styleSheet() == 'background-color: rgba(255,0,0,0.5);'
    assert before_slider_value == windows_container.output_window.slider.value()
    assert before_cur_frame_no == app_thread.mon.state.preview_window_output.current_frame_no

    enter_time_in_go_to_dialog_box(app_thread,'0:01:30.00')

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2
    expected_cur_frame = 4 * 90

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.49, 0.51), current_frame_no=expected_cur_frame, is_output_window=True, restrict_frame_interval=False, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))
