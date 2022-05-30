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

def test_go_to_restricted(app_thread, windows_container: WindowsContainer, blank_state):
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

    # open_clip_on_output_window(app_thread, windows_container, '0:01:00.00', '0:02:00.00', get_blank_1hr_vid_path())

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    press_space_to_pause(windows_container.output_window)
    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == expected_in_frame)

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.12, 0.13), current_frame_no=expected_in_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
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

def test_video_stops_at_out_with_restrict_with_keyboard(app_thread, windows_container: WindowsContainer, blank_state):
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

    enter_time_in_go_to_dialog_box(app_thread, '0:01:59.02')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 60 * 2 - 2)

    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 60 * 2 - 1)
    pyautogui.press('right')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 60 * 2)

    # should not change frame
    pyautogui.press('right')
    time.sleep(2)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 60 * 2)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

def test_video_stops_at_out_with_restrict_with_mouse(app_thread, windows_container: WindowsContainer, blank_state):
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

    enter_time_in_go_to_dialog_box(app_thread, '0:01:59.00')
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 60 * 2 - 4)
    
    go_to_prev_wind_slider(windows_container.output_window, 0.5)
    pyautogui.scroll(-1)
    wait_until(lambda: app_thread.mon.state.preview_window_output.current_frame_no == 4 * 60 * 2)

    expected_in_frame = 4 * 60 * 1
    expected_out_frame = 4 * 60 * 2

    clip = get_video_clip_for_1hr_vid(in_frame=expected_in_frame, out_frame=expected_out_frame)
    expected_timeline_clips = [(clip,120)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_fn(clip, slider_range=(0.03, 0.04), current_frame_no=expected_out_frame),
                get_assert_preview_fn(clip, slider_range=(0.87, 0.88), current_frame_no=expected_out_frame, is_output_window=True, extra_frames_left=40, extra_frames_right=40), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0))

# go to before in frame
# go to after out frame
# set extra frames to 2 secs, witch to not restricted, should be able to play pass out frame to end
# go to right before end, press right few times and check it went pass out frame
# go to right before end, scroll right and check it went pass out frame
# go to few frames after in frame, press left few times and check it went pass in frame
# go to few frames after in frame, scroll left and check it went pass in frame
# change in frame and timeline should reflect
# change out frame and timeline should reflect
# test clip with only in frame
# test clip with only out frame

