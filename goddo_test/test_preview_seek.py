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
from goddo_player.utils.window_util import get_center_pos_of_widget, local_to_global_pos
from goddo_test.common_asserts import assert_state_is_blank
from goddo_test.utils.assert_utils import *
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.qt_app_thread import QtAppThread
from goddo_test.utils.test_utils import click_on_prev_wind_slider, drag_and_drop, drop_cur_to_timeline, drop_video_on_file_list, drop_video_on_preview, enter_time_in_go_to_dialog_box, get_test_vid_path, get_video_clip_for_1hr_vid, go_to_prev_wind_slider, save_screenshot, wait_until, pil_img_to_arr, cmp_image
from goddo_test.utils.windows_container import WindowsContainer

def test_preview_go_to_dialog_with_keyboard(app_thread, windows_container: WindowsContainer, blank_state):
    # test nothing happens if we push g without video loaded
    pyautogui.click(*get_center_pos_of_widget(windows_container.preview_window))
    wait_until(lambda: windows_container.preview_window.isActiveWindow())
    pyautogui.press('g')
    time.sleep(0.5)
    wait_until(lambda: windows_container.preview_window.dialog.isHidden())

    video_path = get_blank_1hr_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('g')
    wait_until(lambda: not windows_container.preview_window.dialog.isHidden())

    assert windows_container.preview_window.dialog.value() == app_thread.mon.state.preview_window.current_frame_no

    # test letters are ignored
    pyautogui.press('a')
    assert windows_container.preview_window.dialog.value() == app_thread.mon.state.preview_window.current_frame_no

    # reset back to frame 1
    pyautogui.press('end')
    pyautogui.press('backspace')
    pyautogui.press('backspace')
    pyautogui.press('0')
    pyautogui.press('1')
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.01')

    # test min is frame 1
    pyautogui.press('home')
    pyautogui.press('down')
    time.sleep(0.5)
    assert windows_container.preview_window.dialog.text() == '0:00:00.01'

    # test hour increased
    pyautogui.press('up')
    wait_until(lambda: windows_container.preview_window.dialog.text() == '1:00:00.01')

    # test max is video total length
    pyautogui.press('up')
    wait_until(lambda: windows_container.preview_window.dialog.text() == '1:00:00.02')

    # test hour decreased
    pyautogui.press('down')
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.02')

    # test pos 2, hour increased
    pyautogui.press('right')
    pyautogui.press('up')
    wait_until(lambda: windows_container.preview_window.dialog.text() == '1:00:00.02')
    pyautogui.press('down')
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.02')

    # test pos 3, min increased/decreased
    for _ in range(3):
        pyautogui.press('right')
        pyautogui.press('up')
        wait_until(lambda: windows_container.preview_window.dialog.text() == '0:01:00.02')
        pyautogui.press('down')
        wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.02')

    # test pos 3, secs increased/decreased
    for _ in range(3):
        pyautogui.press('right')
        pyautogui.press('up')
        wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:01.02')
        pyautogui.press('down')
        wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.02')

    # test pos 3, frames increased/decreased
    for _ in range(3):
        pyautogui.press('right')
        pyautogui.press('up')
        wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.03')
        pyautogui.press('down')
        wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.02')

    # test min is 1 frame
    pyautogui.press('down')
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.01')
    pyautogui.press('down')
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.01')

    for _ in range(6):
        pyautogui.press('left')
    for _ in range(4):
        pyautogui.press('up')
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:04:00.01')

    expected_cur_frame_no = 4 * 60 * 4 + 1

    pyautogui.press('enter')
    wait_until(lambda: windows_container.preview_window.dialog.isHidden())
    assert app_thread.mon.state.preview_window.current_frame_no == expected_cur_frame_no

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_1hr_file_fn(slider_range=(0.05, 0.08), current_frame_no=expected_cur_frame_no),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_preview_go_to_dialog_with_mouse(app_thread, windows_container: WindowsContainer, blank_state):
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
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.01')

    font_metrics = windows_container.preview_window.dialog.time_edit.fontMetrics()
    hour_right = font_metrics.width("0:")
    min_width = font_metrics.width("00:")
    min_right = hour_right + min_width
    sec_width = font_metrics.width("00.")
    sec_right = min_right + sec_width

    pt = local_to_global_pos(windows_container.preview_window.dialog.time_edit, windows_container.preview_window.dialog.dialog)
    y = int(pt.y() + windows_container.preview_window.dialog.time_edit.height() / 2)

    # test hour
    pyautogui.moveTo(int(pt.x() + hour_right / 2), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.preview_window.dialog.text() == '1:00:00.01')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.01')

    # test min
    pyautogui.moveTo(int(pt.x() + hour_right + min_width / 2), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:01:00.01')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.01')

    # test sec
    pyautogui.moveTo(int(pt.x() + min_right + sec_width / 2), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:01.01')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.01')

    # test frames
    pyautogui.moveTo(int(pt.x() + sec_right + 5), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.02')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:00:00.01')

    pyautogui.moveTo(int(pt.x() + hour_right + min_width / 2), y )
    for _ in range(4):
        pyautogui.scroll(1)
    wait_until(lambda: windows_container.preview_window.dialog.text() == '0:04:00.01')

    expected_cur_frame_no = 4 * 60 * 4 + 1

    pyautogui.press('enter')
    wait_until(lambda: windows_container.preview_window.dialog.isHidden())
    assert app_thread.mon.state.preview_window.current_frame_no == expected_cur_frame_no

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_1hr_file_fn(slider_range=(0.05, 0.08), current_frame_no=expected_cur_frame_no),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)         

def test_preview_output_go_to_dialog_with_keyboard(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_blank_1hr_vid_path()
    drop_video_on_file_list(app_thread, windows_container, [video_path])

    video_tab_list_widget = app_thread.mon.tabbed_list_window.videos_tab.list_widget
    item = video_tab_list_widget.get_all_items()[0]
    item_widget = video_tab_list_widget.itemWidget(item)
    pt = local_to_global_pos(item_widget, video_tab_list_widget)
    pyautogui.doubleClick(x=pt.x() + 10, y=pt.y() + 10)
    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)
    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    pyautogui.press('g')
    wait_until(lambda: not windows_container.preview_window.dialog.isHidden())

    pyautogui.press('home')
    pyautogui.press('down')
    pyautogui.press('enter')
    wait_until(lambda: windows_container.preview_window.dialog.isHidden())

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)
    drop_cur_to_timeline(windows_container)

    timeline_window = windows_container.timeline_window
    pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    pyautogui.doubleClick(x=pt.x() + 50 + 10, y=pt.y() + 68 + 10)
    wait_until(lambda: windows_container.output_window.preview_widget.cap is not None)

    pyautogui.press('g')
    wait_until(lambda: not windows_container.output_window.dialog.isHidden())

    assert windows_container.output_window.dialog.value() == app_thread.mon.state.preview_window_output.current_frame_no

    # test letters are ignored
    pyautogui.press('home')
    pyautogui.press('a')
    time.sleep(0.5)
    assert windows_container.output_window.dialog.value() == app_thread.mon.state.preview_window_output.current_frame_no

    # test min is frame 1
    pyautogui.press('down')
    time.sleep(0.5)
    assert windows_container.output_window.dialog.text() == '0:00:00.01'

    # test hour increased
    pyautogui.press('up')
    wait_until(lambda: windows_container.output_window.dialog.text() == '1:00:00.01')

    # test max is video total length
    pyautogui.press('up')
    wait_until(lambda: windows_container.output_window.dialog.text() == '1:00:00.02')

    # test hour decreased
    pyautogui.press('down')
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.02')

    # test pos 2, hour increased
    pyautogui.press('right')
    pyautogui.press('up')
    wait_until(lambda: windows_container.output_window.dialog.text() == '1:00:00.02')
    pyautogui.press('down')
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.02')

    # test pos 3, min increased/decreased
    for _ in range(3):
        pyautogui.press('right')
        pyautogui.press('up')
        wait_until(lambda: windows_container.output_window.dialog.text() == '0:01:00.02')
        pyautogui.press('down')
        wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.02')

    # test pos 3, secs increased/decreased
    for _ in range(3):
        pyautogui.press('right')
        pyautogui.press('up')
        wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:01.02')
        pyautogui.press('down')
        wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.02')

    # test pos 3, frames increased/decreased
    for _ in range(3):
        pyautogui.press('right')
        pyautogui.press('up')
        wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.03')
        pyautogui.press('down')
        wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.02')

    # test min is 1 frame
    pyautogui.press('down')
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.01')
    pyautogui.press('down')
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.01')

    for _ in range(6):
        pyautogui.press('left')
    for _ in range(4):
        pyautogui.press('up')
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:04:00.01')

    expected_cur_frame_no = 4 * 60 * 4 + 1

    pyautogui.press('enter')
    wait_until(lambda: windows_container.output_window.dialog.isHidden())
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=1)
    expected_timeline_clips = [(clip,7201)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_1hr_file_fn(slider_range=(0, 0.01), current_frame_no=1, in_frame=1),
                get_assert_preview_fn(clip, slider_range=(0.05, 0.08), current_frame_no=expected_cur_frame_no, is_output_window=True), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0, scroll_area_width=7320))

def test_preview_output_go_to_dialog_with_mouse(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_blank_1hr_vid_path()
    drop_video_on_file_list(app_thread, windows_container, [video_path])

    video_tab_list_widget = app_thread.mon.tabbed_list_window.videos_tab.list_widget
    item = video_tab_list_widget.get_all_items()[0]
    item_widget = video_tab_list_widget.itemWidget(item)
    pt = local_to_global_pos(item_widget, video_tab_list_widget)
    pyautogui.doubleClick(x=pt.x() + 10, y=pt.y() + 10)
    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)
    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    pyautogui.press('g')
    wait_until(lambda: not windows_container.preview_window.dialog.isHidden())

    pyautogui.press('home')
    pyautogui.press('down')
    pyautogui.press('enter')
    wait_until(lambda: windows_container.preview_window.dialog.isHidden())

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)
    drop_cur_to_timeline(windows_container)

    timeline_window = windows_container.timeline_window
    pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    pyautogui.doubleClick(x=pt.x() + 50 + 10, y=pt.y() + 68 + 10)
    wait_until(lambda: windows_container.output_window.preview_widget.cap is not None)

    pyautogui.press('g')
    wait_until(lambda: not windows_container.output_window.dialog.isHidden())

    assert windows_container.output_window.dialog.value() == 1

    pyautogui.press('g')
    wait_until(lambda: not windows_container.output_window.dialog.isHidden())

    font_metrics = windows_container.output_window.dialog.time_edit.fontMetrics()
    hour_right = font_metrics.width("0:")
    min_width = font_metrics.width("00:")
    min_right = hour_right + min_width
    sec_width = font_metrics.width("00.")
    sec_right = min_right + sec_width

    pt = local_to_global_pos(windows_container.output_window.dialog.time_edit, windows_container.output_window.dialog.dialog)
    y = int(pt.y() + windows_container.output_window.dialog.time_edit.height() / 2)

    # test hour
    pyautogui.moveTo(int(pt.x() + hour_right / 2), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.output_window.dialog.text() == '1:00:00.01')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.01')

    # test min
    pyautogui.moveTo(int(pt.x() + hour_right + min_width / 2), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:01:00.01')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.01')

    # test sec
    pyautogui.moveTo(int(pt.x() + min_right + sec_width / 2), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:01.01')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.01')

    # test frames
    pyautogui.moveTo(int(pt.x() + sec_right + 5), y )
    pyautogui.scroll(1)
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.02')
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:00:00.01')

    pyautogui.moveTo(int(pt.x() + hour_right + min_width / 2), y )
    for _ in range(4):
        pyautogui.scroll(1)
    wait_until(lambda: windows_container.output_window.dialog.text() == '0:04:00.01')

    expected_cur_frame_no = 4 * 60 * 4 + 1

    pyautogui.press('enter')
    wait_until(lambda: windows_container.output_window.dialog.isHidden())
    assert app_thread.mon.state.preview_window_output.current_frame_no == expected_cur_frame_no

    clip = get_video_clip_for_1hr_vid(in_frame=1)
    expected_timeline_clips = [(clip,7201)]

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_1hr_file_fn(slider_range=(0, 0.01), current_frame_no=1, in_frame=1),
                get_assert_preview_fn(clip, slider_range=(0.05, 0.08), current_frame_no=expected_cur_frame_no, is_output_window=True), 
                get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0, scroll_area_width=7320))
