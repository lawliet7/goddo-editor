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
from goddo_test.utils.test_utils import drag_and_drop, drop_video_on_preview, get_test_vid_path, wait_until, pil_img_to_arr, cmp_image
from goddo_test.utils.windows_container import WindowsContainer


def test_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    cur_frame_no = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)

    logging.info(f'=== slider value {windows_container.preview_window.slider.value()}')

    generic_assert(app_thread, windows_container, blank_state, 'test_in_frame_save.json',
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(current_frame_no=cur_frame_no, in_frame=cur_frame_no), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)


def test_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    print(app_thread.mon.state.preview_window)
    cur_frame_no = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('o')

    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out is not None)

    generic_assert(app_thread, windows_container, blank_state, 'test_out_frame_save.json',
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(out_frame=cur_frame_no), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)


def test_in_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('space')

    time.sleep(0.5)

    pyautogui.press('space')

    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())
    out_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('o')

    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out is not None)

    time.sleep(0.5)

    generic_assert(app_thread, windows_container, blank_state, 'test_in_out_frame_save.json',
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.1, 0.3), in_frame=in_frame, out_frame=out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)


def test_unset_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    # in_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('space')

    time.sleep(0.5)

    pyautogui.press('space')

    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())
    out_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out is not None)

    with pyautogui.hold('shift'):
        pyautogui.press(['i'])

    generic_assert(app_thread, windows_container, blank_state, 'test_unset_in_frame_save.json',
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.1, 0.3), out_frame=out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)


def test_unset_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('space')

    time.sleep(0.5)

    pyautogui.press('space')

    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())
    out_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out is not None)

    with pyautogui.hold('shift'):
        pyautogui.press(['o'])

    time.sleep(0.5)

    generic_assert(app_thread, windows_container, blank_state, 'test_unset_out_frame_save.json',
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.1, 0.3), current_frame_no=out_frame, in_frame=in_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)


def test_unset_in_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    # in_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('space')

    time.sleep(0.5)

    pyautogui.press('space')

    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())
    out_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out is not None)

    with pyautogui.hold('shift'):
        pyautogui.press(['o'])

    time.sleep(0.5)

    with pyautogui.hold('shift'):
        pyautogui.press(['i'])

    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is None)

    time.sleep(0.5)

    generic_assert(app_thread, windows_container, blank_state, 'test_unset_in_out_frame.json',
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(0.1, 0.3), current_frame_no=out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)


def test_go_to_in_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)

    slider = windows_container.preview_window.slider

    cur_slider_value = slider.value()

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('space')

    time.sleep(0.5)

    pyautogui.press('space')

    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())
    out_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('o')

    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out is not None)
    
    pos = local_to_global_pos(slider, windows_container.preview_window)
    x_offset = int(slider.width() * 0.9)
    y_offset = int(slider.height() * 0.5)
    pyautogui.moveTo(pos.x() + x_offset, pos.y() + y_offset)
    pyautogui.click()

    wait_until(lambda: slider.value() > cur_slider_value)

    pyautogui.press('[')

    wait_until(lambda: slider.value() == cur_slider_value)

    expected_slider_pct = cur_slider_value/200
    generic_assert(app_thread, windows_container, blank_state, 'test_go_to_in_frame.json',
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(expected_slider_pct-0.01, expected_slider_pct+0.01), current_frame_no=in_frame, in_frame=in_frame, out_frame=out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)


def test_go_to_out_frame(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)

    slider = windows_container.preview_window.slider

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('space')

    time.sleep(0.5)

    pyautogui.press('space')

    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())
    out_frame = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('o')

    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out is not None)

    cur_slider_value = slider.value()
    
    pos = local_to_global_pos(slider, windows_container.preview_window)
    x_offset = int(slider.width() * 0.9)
    y_offset = int(slider.height() * 0.5)
    pyautogui.moveTo(pos.x() + x_offset, pos.y() + y_offset)
    pyautogui.click()

    wait_until(lambda: slider.value() > cur_slider_value)

    pyautogui.press(']')

    wait_until(lambda: slider.value() == cur_slider_value)

    expected_slider_pct = cur_slider_value/200
    generic_assert(app_thread, windows_container, blank_state, 'test_go_to_out_frame.json',
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(slider_range=(expected_slider_pct-0.01, expected_slider_pct+0.01), current_frame_no=out_frame, in_frame=in_frame, out_frame=out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            assert_blank_timeline)
