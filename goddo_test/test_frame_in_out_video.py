import re
import time

import pyautogui
from PyQt5.QtCore import QUrl

from goddo_player.utils.video_path import VideoPath
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.common_asserts import assert_state_is_blank
from goddo_test.utils.assert_utils import *
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.test_utils import click_on_prev_wind_slider, drag_and_drop, drop_video_on_preview, enter_time_in_go_to_dialog_box, get_test_vid_path, go_to_prev_wind_slider, open_clip_on_output_window, wait_until, pil_img_to_arr, cmp_image
from goddo_test.utils.windows_container import WindowsContainer

frames_1_sec = 30
frames_3_sec = int(round(29.97 * 3))
frames_5_sec = int(round(29.97 * 5))

def test_in_frame_when_no_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_1_sec)

    logging.info(f'=== slider value {windows_container.preview_window.slider.value()}')

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.14, 0.15), current_frame_no=frames_1_sec, in_frame=frames_1_sec), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_in_frame_before_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_3_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_1_sec)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.14, 0.15), current_frame_no=frames_1_sec, in_frame=frames_1_sec, out_frame=frames_3_sec), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_in_frame_after_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_1_sec)
    
    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_3_sec)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.42, 0.43), current_frame_no=frames_3_sec, in_frame=frames_3_sec), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_change_in_frame_before_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')
    
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_5_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_1_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_3_sec)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.42, 0.43), current_frame_no=frames_3_sec, in_frame=frames_3_sec, out_frame=frames_5_sec), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_change_in_frame_from_before_to_after_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_3_sec)
    
    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_1_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_5_sec)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.71, 0.72), current_frame_no=frames_5_sec, in_frame=frames_5_sec), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)


def test_out_frame_when_no_in(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_3_sec)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.42, 0.43), out_frame=frames_3_sec), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_out_frame_after_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_1_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_3_sec)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.42, 0.43), in_frame=frames_1_sec, out_frame=frames_3_sec), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_out_frame_before_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_3_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_1_sec)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.14, 0.15), out_frame=frames_1_sec), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_change_out_frame_from_after_to_before_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_3_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_5_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_1_sec)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.14, 0.15), out_frame=frames_1_sec), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)


def test_unset_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_3_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_5_sec)

    with pyautogui.hold('shift'):
        pyautogui.press(['i'])
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is None)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.71, 0.72), out_frame=frames_5_sec), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)


def test_unset_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_3_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_5_sec)

    with pyautogui.hold('shift'):
        pyautogui.press(['o'])
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is None)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.71, 0.72), current_frame_no=frames_5_sec, in_frame=frames_3_sec), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)


def test_unset_in_then_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_3_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_5_sec)

    with pyautogui.hold('shift'):
        pyautogui.press(['i'])
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is None)

    with pyautogui.hold('shift'):
        pyautogui.press(['o'])
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is None)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.71, 0.72), current_frame_no=frames_5_sec), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)

def test_unset_out_then_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:03.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_3_sec)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_5_sec)

    with pyautogui.hold('shift'):
        pyautogui.press(['o'])
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is None)

    with pyautogui.hold('shift'):
        pyautogui.press(['i'])
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is None)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.71, 0.72), current_frame_no=frames_5_sec), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)


def test_go_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_1_sec)

    click_on_prev_wind_slider(windows_container.preview_window, 0.8)
    wait_until(lambda: app_thread.mon.state.preview_window.current_frame_no > frames_1_sec)

    pyautogui.press('[')
    wait_until(lambda: app_thread.mon.state.preview_window.current_frame_no == frames_1_sec)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.14, 0.15), current_frame_no=frames_1_sec, in_frame=frames_1_sec), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)

def test_go_to_in_frame_when_no_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')

    pyautogui.press('[')

    time.sleep(0.5)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.14, 0.15), current_frame_no=frames_1_sec), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)

def test_go_to_in_frame_when_only_out(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    click_on_prev_wind_slider(windows_container.preview_window, 0.95)

    pyautogui.press('o')

    out_frame = windows_container.preview_window.state.preview_window.current_frame_no

    click_on_prev_wind_slider(windows_container.preview_window, 0.05)

    frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    pyautogui.press('[')

    time.sleep(0.5)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.03, 0.07), current_frame_no=frame_no, out_frame=out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)           

def test_go_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame == frames_5_sec)

    click_on_prev_wind_slider(windows_container.preview_window, 0.2)
    wait_until(lambda: app_thread.mon.state.preview_window.current_frame_no < frames_5_sec)

    pyautogui.press(']')
    wait_until(lambda: app_thread.mon.state.preview_window.current_frame_no == frames_5_sec)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.71, 0.72), current_frame_no=frames_5_sec, out_frame=frames_5_sec), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)

def test_go_to_out_frame_when_no_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:05.00')

    pyautogui.press(']')

    time.sleep(0.5)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.71, 0.72), current_frame_no=frames_5_sec), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)

def test_go_to_out_frame_when_only_in(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:00:01.00')
    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame == frames_1_sec)

    pyautogui.press(']')

    time.sleep(0.5)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.14, 0.15), current_frame_no=frames_1_sec, in_frame=frames_1_sec), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)
