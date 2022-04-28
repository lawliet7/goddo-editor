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
from goddo_test.utils.test_utils import click_on_prev_wind_slider, drag_and_drop, get_test_vid_path, save_reload_and_assert_state, save_screenshot, wait_until, pil_img_to_arr, cmp_image
from goddo_test.utils.windows_container import WindowsContainer

def test_slider_disabled_initially(windows_container: WindowsContainer):
    assert not windows_container.preview_window.slider.isEnabled()

    click_on_prev_wind_slider(windows_container.preview_window, 0.9, should_slider_value_change=False)

    assert windows_container.preview_window.preview_widget.frame_pixmap is None
    assert windows_container.preview_window.slider.value() == 0


def test_while_playing_seek_on_slider(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    img_base = pil_img_to_arr(pyautogui.screenshot())

    pyautogui.press('space')
    wait_until(lambda: windows_container.preview_window.preview_widget.timer.isActive())

    click_on_prev_wind_slider(windows_container.preview_window, 0.9)

    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    time.sleep(0.5)

    img_new = pil_img_to_arr(pyautogui.screenshot())

    assert cmp_image(img_base, img_new) < 0.98

    _, _, secs, frames = time_str_to_components(windows_container.preview_window.label.text()[:10])
    assert secs == 6
    assert 5 <= frames <= 15

    generic_assert(app_thread, windows_container, blank_state, 'test_out_frame_save.json',
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.89, 1)), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_while_paused_seek_on_slider(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    img_base = pil_img_to_arr(pyautogui.screenshot())

    click_on_prev_wind_slider(windows_container.preview_window, 0.9)

    logging.info(f'slider value {windows_container.preview_window.slider.value()}')
    img_new = pil_img_to_arr(pyautogui.screenshot())

    assert cmp_image(img_base, img_new) < 0.98

    _, _, secs, frames = time_str_to_components(windows_container.preview_window.label.text()[:10])
    assert secs == 6
    assert 5 <= frames <= 15

    generic_assert(app_thread, windows_container, blank_state, 'test_while_paused_seek_on_slider.json',
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.89, 0.91)), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_skip_ahead_to_end(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    click_on_prev_wind_slider(windows_container.preview_window, 0.7)

    slider = windows_container.preview_window.slider
    pos = local_to_global_pos(slider, windows_container.preview_window)
    x_offset = int(slider.width() * 0.1)
    y_offset = int(slider.height() * 0.5)
    pyautogui.moveTo(pos.x() + x_offset, pos.y() + y_offset)
    pyautogui.scroll(-1)

    wait_until(lambda: old_frame_no < windows_container.preview_window.state.preview_window.current_frame_no)

    generic_assert(app_thread, windows_container, blank_state, 'test_skip_ahead.json',
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.9, 1), is_max_speed=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_skip_ahead(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    slider = windows_container.preview_window.slider
    pos = local_to_global_pos(slider, windows_container.preview_window)
    x_offset = int(slider.width() * 0.1)
    y_offset = int(slider.height() * 0.5)
    pyautogui.moveTo(pos.x() + x_offset, pos.y() + y_offset)
    pyautogui.scroll(-1)

    wait_until(lambda: old_frame_no < windows_container.preview_window.state.preview_window.current_frame_no)

    generic_assert(app_thread, windows_container, blank_state, 'test_skip_ahead.json',
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.7, 0.9), is_max_speed=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_skip_before_to_beginning(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    slider = windows_container.preview_window.slider
    pos = local_to_global_pos(slider, windows_container.preview_window)
    x_offset = int(slider.width() * 0.1)
    y_offset = int(slider.height() * 0.5)
    pyautogui.moveTo(pos.x() + x_offset, pos.y() + y_offset)
    pyautogui.scroll(1)

    wait_until(lambda: old_frame_no > windows_container.preview_window.state.preview_window.current_frame_no)

    generic_assert(app_thread, windows_container, blank_state, 'test_skip_before_to_beginning.json',
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.0, 0.1), is_max_speed=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_skip_before(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    click_on_prev_wind_slider(windows_container.preview_window, 0.9)

    slider = windows_container.preview_window.slider
    pos = local_to_global_pos(slider, windows_container.preview_window)
    x_offset = int(slider.width() * 0.1)
    y_offset = int(slider.height() * 0.5)
    pyautogui.moveTo(pos.x() + x_offset, pos.y() + y_offset)
    pyautogui.scroll(1)

    wait_until(lambda: old_frame_no < windows_container.preview_window.state.preview_window.current_frame_no)

    generic_assert(app_thread, windows_container, blank_state, 'test_skip_before_to_beginning.json',
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.15, 0.25), is_max_speed=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_switch_to_max_speed(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('s')
    pyautogui.press('space')

    time.sleep(1)

    pyautogui.press('space')

    time.sleep(3)

def drop_video_on_preview(app_thread, windows_container, video_path):
    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    app_thread.cmd.submit_cmd(Command(CommandType.ADD_ITEM_DND_WINDOW, [video_path.str()]))

    dnd_widget = app_thread.cmd.dnd_widget

    item_idx = dnd_widget.get_count() - 1
    _, item_widget = dnd_widget.get_item_and_widget(item_idx)

    src_corner_pt = dnd_widget.item_widget_pos(item_idx)
    src_pt_x = src_corner_pt.x() + 10
    src_pt_y = src_corner_pt.y() + int(item_widget.size().height() / 2)

    dest_corner_pt = local_to_global_pos(windows_container.preview_window.preview_widget, windows_container.preview_window)
    dest_pt_x = dest_corner_pt.x() + 10
    dest_pt_y = dest_corner_pt.y() + 10

    # win_rect = windows_container.preview_window.geometry().getRect()
    # base_img = pil_img_to_arr(pyautogui.screenshot(region=win_rect))

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)

    pyautogui.press('space')

    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())
