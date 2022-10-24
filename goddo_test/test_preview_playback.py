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
from goddo_test.utils.test_utils import click_on_prev_wind_slider, drag_and_drop, drop_video_on_preview, enter_time_in_go_to_dialog_box, get_test_vid_path, go_to_prev_wind_slider, grab_screenshot, save_screenshot, wait_until, pil_img_to_arr, cmp_image
from goddo_test.utils.windows_container import WindowsContainer

def test_slider_disabled_initially(windows_container: WindowsContainer):
    assert not windows_container.preview_window.slider.isEnabled()

    click_on_prev_wind_slider(windows_container.preview_window, 0.9, should_slider_value_change=False)

    assert windows_container.preview_window.preview_widget.frame_pixmap is None
    assert windows_container.preview_window.slider.value() == 0


def test_while_playing_seek_on_slider(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    # img_base = pil_img_to_arr(pyautogui.screenshot())
    old_frame_pixmap = windows_container.preview_window.preview_widget.frame_pixmap

    pyautogui.press('space')
    wait_until(lambda: windows_container.preview_window.preview_widget.timer.isActive())

    click_on_prev_wind_slider(windows_container.preview_window, 0.9)

    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    time.sleep(0.5)

    # img_new = pil_img_to_arr(pyautogui.screenshot())

    # assert cmp_image(img_base, img_new) < 0.98

    wait_until(lambda: old_frame_pixmap != windows_container.preview_window.preview_widget.frame_pixmap)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.89, 1)), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_while_paused_seek_on_slider(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    old_frame_pixmap = windows_container.preview_window.preview_widget.frame_pixmap

    # img_base = grab_screenshot()
    # save_screenshot('before.png', img_base)

    click_on_prev_wind_slider(windows_container.preview_window, 0.9)

    # logging.info(f'slider value {windows_container.preview_window.slider.value()}')
    # img_new = grab_screenshot()
    # save_screenshot('after.png', img_new)

    # new_frame_pixmap = windows_container.preview_window.preview_widget.frame_pixmap

    wait_until(lambda: old_frame_pixmap != windows_container.preview_window.preview_widget.frame_pixmap)

    # assert cmp_image(img_base, img_new) < 0.98

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.89, 0.91)), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_skip_ahead_to_end(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    click_on_prev_wind_slider(windows_container.preview_window, 0.7)
    pyautogui.scroll(-1)

    wait_until(lambda: old_frame_no < windows_container.preview_window.state.preview_window.current_frame_no)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.99, 1), is_max_speed=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_skip_ahead(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    go_to_prev_wind_slider(windows_container.preview_window, 0.1)
    pyautogui.scroll(-1)

    wait_until(lambda: old_frame_no < windows_container.preview_window.state.preview_window.current_frame_no)

    slider_range = get_slider_range(windows_container, old_frame_no, is_fwd=True, threshold=0.01)
    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=slider_range, is_max_speed=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_skip_before_to_beginning(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    go_to_prev_wind_slider(windows_container.preview_window, 0.1)
    pyautogui.scroll(1)

    wait_until(lambda: old_frame_no > windows_container.preview_window.state.preview_window.current_frame_no)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.0, 0.01), is_max_speed=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_skip_before(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    click_on_prev_wind_slider(windows_container.preview_window, 0.9)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    pyautogui.scroll(1)

    wait_until(lambda: old_frame_no > windows_container.preview_window.state.preview_window.current_frame_no)

    slider_range = get_slider_range(windows_container, old_frame_no, is_fwd=False, threshold=0.01)
    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=slider_range, is_max_speed=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_switch_to_max_speed(app_thread, windows_container: WindowsContainer, blank_state):
    def play_for_one_sec():
        pyautogui.press('space')
        time.sleep(1)
        pyautogui.press('space')
        wait_until(lambda: not windows_container.preview_window.is_playing() and old_frame_no < windows_container.preview_window.state.preview_window.current_frame_no)

    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    pyautogui.press('i')

    play_for_one_sec()

    new_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    pyautogui.press('[')
    wait_until(lambda: old_frame_no == windows_container.preview_window.state.preview_window.current_frame_no)

    pyautogui.press('s')
    play_for_one_sec()

    super_new_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    logging.info(f'=== old frame no {old_frame_no} new frame no {new_frame_no} super new frame no {super_new_frame_no}')

    assert (super_new_frame_no - old_frame_no) > ((new_frame_no - old_frame_no) * 1.5) # at least 10% faster than normal

    slider_value_pct = windows_container.preview_window.slider.value() / 200

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(slider_value_pct-0.01, slider_value_pct+0.01), is_max_speed=True, in_frame=old_frame_no), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_skip_ahead_10s(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    go_to_prev_wind_slider(windows_container.preview_window, 0.1)
    pyautogui.scroll(1)

    wait_until(lambda: windows_container.preview_window.state.preview_window.current_frame_no == 1)
    
    assert check_skip_label(windows_container) == 'skip=5s'

    pyautogui.press('add')

    wait_until(lambda: check_skip_label(windows_container) == 'skip=10s')

    pyautogui.scroll(-1)

    wait_until(lambda: windows_container.preview_window.state.preview_window.current_frame_no == 210)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.99, 1), current_frame_no=210, time_skip_label="10s"), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_skip_before_10s(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    click_on_prev_wind_slider(windows_container.preview_window, 0.9)
    pyautogui.scroll(-1)
    wait_until(lambda: windows_container.preview_window.state.preview_window.current_frame_no == 210)
    
    assert check_skip_label(windows_container) == 'skip=5s'

    pyautogui.press('add') # numpad+

    wait_until(lambda: check_skip_label(windows_container) == 'skip=10s')

    pyautogui.scroll(1)

    wait_until(lambda: windows_container.preview_window.state.preview_window.current_frame_no == 1)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0, 0.01), current_frame_no=1, time_skip_label="10s"), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_capped_time_skip_multiplier_to_5m(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)
    
    assert check_skip_label(windows_container) == 'skip=5s'

    for _ in range(12):
        pyautogui.press('add') # numpad+

    wait_until(lambda: check_skip_label(windows_container) == 'skip=1m5s')

    for _ in range(12*5-1):
        pyautogui.press('add') # numpad+

    wait_until(lambda: check_skip_label(windows_container) == 'skip=5m')

    pyautogui.press('add') # numpad+

    wait_until(lambda: check_skip_label(windows_container) == 'skip=5m')

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(time_skip_label="5m"), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_floored_time_skip_multiplier_to_5s(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)
    
    assert check_skip_label(windows_container) == 'skip=5s'

    pyautogui.press('add') # numpad+
    pyautogui.press('add') # numpad+
    pyautogui.press('add') # numpad+

    wait_until(lambda: check_skip_label(windows_container) == 'skip=20s')

    pyautogui.press('subtract') # numpad-

    wait_until(lambda: check_skip_label(windows_container) == 'skip=15s')

    pyautogui.press('subtract') # numpad-
    pyautogui.press('subtract') # numpad-

    assert check_skip_label(windows_container) == 'skip=5s'

    pyautogui.press('subtract') # numpad-

    assert check_skip_label(windows_container) == 'skip=5s'

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_advance_frame_with_right_key(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)
    
    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no
    old_slider_pct = windows_container.preview_window.slider.value() / 200

    pyautogui.press('right')

    wait_until(lambda: old_frame_no < windows_container.preview_window.state.preview_window.current_frame_no)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(old_slider_pct, old_slider_pct+0.01), current_frame_no=old_frame_no+1),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_move_5_frames_back_with_left_key(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)
    
    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no
    old_slider_pct = windows_container.preview_window.slider.value() / 200

    pyautogui.press('left')

    wait_until(lambda: old_frame_no > windows_container.preview_window.state.preview_window.current_frame_no)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(old_slider_pct-5/210-0.01, old_slider_pct), current_frame_no=old_frame_no-5),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_play_to_end(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    click_on_prev_wind_slider(windows_container.preview_window, 0.95)
    pyautogui.press('space')
    time.sleep(2) # let it play to end and should not fail

    wait_until(lambda: windows_container.preview_window.state.preview_window.current_frame_no == 210)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.99, 1), current_frame_no=210),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_advance_next_frame_at_end_should_do_nothing(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, "0:00:06.29")
    pyautogui.press('right')
    wait_until(lambda: windows_container.preview_window.state.preview_window.current_frame_no == 210)

    pyautogui.press('right')
    time.sleep(0.5)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0.99, 1), current_frame_no=210),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def test_go_back_prev_5_frames_at_beginning_should_do_nothing(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    click_on_prev_wind_slider(windows_container.preview_window, 0.02)

    wait_until(lambda: windows_container.preview_window.state.preview_window.current_frame_no < old_frame_no)

    old_frame_no = windows_container.preview_window.state.preview_window.current_frame_no

    pyautogui.press('left')

    wait_until(lambda: windows_container.preview_window.state.preview_window.current_frame_no < old_frame_no)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(slider_range=(0, 0.01), current_frame_no=1),
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def check_skip_label(windows_container):
    return windows_container.preview_window.skip_label.text()

def get_slider_range(windows_container, old_frame_no, is_fwd, wheel_amt = 5, threshold = 0.01):
    fps = windows_container.preview_window.state.preview_window.fps
    total_frames = windows_container.preview_window.state.preview_window.total_frames
    increment_amt = wheel_amt * fps if is_fwd else -wheel_amt * fps
    est_frame_pct = round(max(min(old_frame_no + increment_amt, total_frames),0) / total_frames, 3)
    slider_range = (max(est_frame_pct - threshold,0), min(est_frame_pct + threshold, 200))
    logging.info(f'=== slider value {windows_container.preview_window.slider.value()}, range {slider_range},' +
                   ' total_frames {total_frames}, fps {fps} est_frame_pct {est_frame_pct} old_frame_no {old_frame_no}')
    return slider_range

def test_save_should_not_flip_speed(app_thread, windows_container: WindowsContainer, blank_state):
    file_name, method_name = get_current_method_name(1)
    save_file_path = my_test_output_folder_path().joinpath(f'{file_name}.{method_name}.json').resolve()
    logging.info(save_file_path)
    save_path_vid_url = VideoPath(file_to_url(str(save_file_path)))
    app_thread.cmd.submit_cmd(Command(CommandType.LOAD_FILE, [save_path_vid_url]))

    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    video_path = get_test_vid_path()
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

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    wait_until(lambda: windows_container.preview_window.preview_widget.frame_pixmap is not None)

    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    assert app_thread.mon.state.preview_window.is_max_speed == False

    with pyautogui.hold('ctrl'):
        pyautogui.press('s')
    time.sleep(0.5)

    assert app_thread.mon.state.preview_window.is_max_speed == False

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_test_file_1_fn(), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)
