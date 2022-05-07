import logging
import re
import time
from numpy import save

import pyautogui
from PyQt5.QtCore import QUrl
from goddo_player.utils.time_frame_utils import time_str_to_components, time_str_to_frames

from goddo_player.utils.video_path import VideoPath
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.common_asserts import assert_state_is_blank
from goddo_test.utils.assert_utils import *
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.qt_app_thread import QtAppThread
from goddo_test.utils.test_utils import click_on_prev_wind_slider, drag_and_drop, drop_video_on_preview, get_test_vid_path, go_to_prev_wind_slider, save_reload_and_assert_state, save_screenshot, wait_until, pil_img_to_arr, cmp_image
from goddo_test.utils.windows_container import WindowsContainer

def test_go_to_dialog_with_keyboard(app_thread, windows_container: WindowsContainer, blank_state):
    # test nothing happens if we push g without video loaded
    pyautogui.press('g')
    time.sleep(0.5)
    wait_until(lambda: windows_container.preview_window.dialog.isHidden())

    video_path = get_blank_1hr_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('g')
    wait_until(lambda: not windows_container.preview_window.dialog.isHidden())

    assert windows_container.preview_window.time_edit.value() == app_thread.mon.state.preview_window.current_frame_no, 'initial state should be current timeframe'

    # test letters are ignored
    pyautogui.press('a')
    assert windows_container.preview_window.time_edit.value() == app_thread.mon.state.preview_window.current_frame_no

    # reset back to frame 1
    pyautogui.press('end')
    pyautogui.press('backspace')
    pyautogui.press('backspace')
    pyautogui.press('0')
    pyautogui.press('1')
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.01')

    # test min is frame 1
    pyautogui.press('home')
    pyautogui.press('down')
    time.sleep(0.5)
    assert windows_container.preview_window.time_edit.text() == '0:00:00.01'

    # test hour increased
    pyautogui.press('up')
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '1:00:00.01')

    # test max is video total length
    pyautogui.press('up')
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '1:00:00.02')

    # test hour decreased
    pyautogui.press('down')
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.02')

    # test pos 2, hour increased
    pyautogui.press('right')
    pyautogui.press('up')
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '1:00:00.02')
    pyautogui.press('down')
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.02')

    # test pos 3, min increased/decreased
    for _ in range(3):
        pyautogui.press('right')
        pyautogui.press('up')
        wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:01:00.02')
        pyautogui.press('down')
        wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.02')

    # test pos 3, secs increased/decreased
    for _ in range(3):
        pyautogui.press('right')
        pyautogui.press('up')
        wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:01.02')
        pyautogui.press('down')
        wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.02')

    # test pos 3, frames increased/decreased
    for _ in range(3):
        pyautogui.press('right')
        pyautogui.press('up')
        wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.03')
        pyautogui.press('down')
        wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.02')

    # test min is 1 frame
    pyautogui.press('down')
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.01')
    pyautogui.press('down')
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.01')

    for _ in range(6):
        pyautogui.press('left')
    for _ in range(4):
        pyautogui.press('up')
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:04:00.01')

    expected_cur_frame_no = 4 * 60 * 4 + 1

    pyautogui.press('enter')
    wait_until(lambda: windows_container.preview_window.dialog.isHidden())
    assert app_thread.mon.state.preview_window.current_frame_no == expected_cur_frame_no

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_1hr_file_fn(slider_range=(0.05, 0.08), current_frame_no=expected_cur_frame_no),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_go_to_dialog_with_mouse(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_blank_1hr_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('g')
    wait_until(lambda: not windows_container.preview_window.dialog.isHidden())

    # reset back to frame 1
    pyautogui.press('end')
    pyautogui.press('backspace')
    pyautogui.press('backspace')
    pyautogui.press('0')
    pyautogui.press('1')
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.01')

    font_metrics = windows_container.preview_window.time_edit.fontMetrics()
    hour_right = font_metrics.width("0:")
    min_width = font_metrics.width("00:")
    min_right = hour_right + min_width
    sec_width = font_metrics.width("00.")
    sec_right = min_right + sec_width

    pt = local_to_global_pos(windows_container.preview_window.time_edit, windows_container.preview_window.dialog)
    y = int(pt.y() + windows_container.preview_window.time_edit.height() / 2)

    # test hour
    pyautogui.moveTo(int(pt.x() + hour_right / 2), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '1:00:00.01')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.01')

    # test min
    pyautogui.moveTo(int(pt.x() + hour_right + min_width / 2), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:01:00.01')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.01')

    # test sec
    pyautogui.moveTo(int(pt.x() + min_right + sec_width / 2), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:01.01')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.01')

    # test frames
    pyautogui.moveTo(int(pt.x() + sec_right + 5), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.02')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:00:00.01')

    pyautogui.moveTo(int(pt.x() + hour_right + min_width / 2), y )
    for _ in range(4):
        pyautogui.scroll(1)
    wait_until(lambda: windows_container.preview_window.time_edit.text() == '0:04:00.01')

    expected_cur_frame_no = 4 * 60 * 4 + 1

    pyautogui.press('enter')
    wait_until(lambda: windows_container.preview_window.dialog.isHidden())
    assert app_thread.mon.state.preview_window.current_frame_no == expected_cur_frame_no

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_1hr_file_fn(slider_range=(0.05, 0.08), current_frame_no=expected_cur_frame_no),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)         
