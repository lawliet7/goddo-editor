import re
import time

import pyautogui
from PyQt5.QtCore import QUrl

from goddo_player.utils.video_path import VideoPath
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.common_asserts import assert_state_is_blank
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.test_utils import drag_and_drop, get_test_vid_path, wait_until, pil_img_to_arr, cmp_image
from goddo_test.utils.windows_container import WindowsContainer


def test_in_frame(app_thread, windows_container: WindowsContainer):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    cur_frame_no = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)

    save_file_path = my_test_output_folder_path().joinpath(f'test_in_frame_save.json').resolve()
    save_path = VideoPath(file_to_url(str(save_file_path)))
    assert_save_reload_assert_again(app_thread, windows_container, video_path, save_path, cur_frame_no, cur_frame_no, None)


def test_out_frame(app_thread, windows_container: WindowsContainer):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())
    # time.sleep(3)

    print(app_thread.mon.state.preview_window)
    cur_frame_no = app_thread.mon.state.preview_window.current_frame_no

    pyautogui.press('o')

    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out is not None)

    save_file_path = my_test_output_folder_path().joinpath(f'test_out_frame_save.json').resolve()
    save_path = VideoPath(file_to_url(str(save_file_path)))
    assert_save_reload_assert_again(app_thread, windows_container, video_path, save_path, None, None, cur_frame_no)


def test_in_out_frame(app_thread, windows_container: WindowsContainer):
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

    save_file_path = my_test_output_folder_path().joinpath(f'test_in_out_frame_save.json').resolve()
    save_path = VideoPath(file_to_url(str(save_file_path)))
    assert_save_reload_assert_again(app_thread, windows_container, video_path, save_path, None, in_frame, out_frame)


def test_unset_in_frame(app_thread, windows_container: WindowsContainer):
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

    save_file_path = my_test_output_folder_path().joinpath(f'test_unset_in_frame_save.json').resolve()
    save_path = VideoPath(file_to_url(str(save_file_path)))
    assert_save_reload_assert_again(app_thread, windows_container, video_path, save_path, None, None, out_frame)


def test_unset_out_frame(app_thread, windows_container: WindowsContainer):
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

    save_file_path = my_test_output_folder_path().joinpath(f'test_unset_out_frame_save.json').resolve()
    save_path = VideoPath(file_to_url(str(save_file_path)))
    assert_save_reload_assert_again(app_thread, windows_container, video_path, save_path, out_frame, in_frame, None)


def test_unset_in_out_frame(app_thread, windows_container: WindowsContainer):
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

    save_file_path = my_test_output_folder_path().joinpath(f'test_unset_in_out_frame.json').resolve()
    save_path = VideoPath(file_to_url(str(save_file_path)))
    assert_save_reload_assert_again(app_thread, windows_container, video_path, save_path, out_frame, None, None)


def test_go_to_in_frame(app_thread, windows_container: WindowsContainer):
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


def test_go_to_out_frame(app_thread, windows_container: WindowsContainer):
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


def assert_save_reload_assert_again(app_thread, windows_container, video_path, save_path, current_frame_no, in_frame, out_frame):
    assert_after_in_out(app_thread, windows_container, video_path, current_frame_no, in_frame, out_frame)

    app_thread.cmd.submit_cmd(Command(CommandType.SAVE_FILE, [save_path]))

    app_thread.cmd.submit_cmd(Command(CommandType.RESET))

    wait_until(lambda: windows_container.preview_window.preview_widget.cap is None)

    assert_state_is_blank(app_thread, windows_container)

    app_thread.cmd.submit_cmd(Command(CommandType.LOAD_FILE, [save_path]))

    assert_after_in_out(app_thread, windows_container, video_path, current_frame_no, in_frame, out_frame)


def assert_after_in_out(app_thread, windows_container, video_path, current_frame_no=None, in_frame=None, out_frame=None):
    # asserts
    assert windows_container.preview_window.label.text() != 'you suck'

    # label should be like 0:00:0X.XX/0:00:07:00
    assert re.match('0:00:0[0-9]\\.[0-9]{2}/0:00:07\\.00', windows_container.preview_window.label.text()[:21])

    assert windows_container.preview_window.slider.value() > 0
    assert windows_container.preview_window.slider.isEnabled()
    assert windows_container.preview_window.windowTitle().endswith(f'- {video_path.file_name(include_ext=False)}')
    assert windows_container.preview_window.preview_widget.frame_pixmap
    assert windows_container.preview_window.preview_widget.get_cur_frame_no() == (current_frame_no or out_frame or in_frame)

    # asert everything inside state
    assert app_thread.mon.state.preview_window.name == 'source'
    assert app_thread.mon.state.preview_window.video_path == video_path
    assert round(app_thread.mon.state.preview_window.fps, 2) == 29.97
    assert app_thread.mon.state.preview_window.total_frames == 210
    assert app_thread.mon.state.preview_window.frame_in_out == FrameInOut(in_frame, out_frame)
    assert app_thread.mon.state.preview_window.current_frame_no == (current_frame_no or out_frame or in_frame)
    assert not app_thread.mon.state.preview_window.is_max_speed
    assert app_thread.mon.state.preview_window.time_skip_multiplier == 1
    assert app_thread.mon.state.preview_window.cur_total_frames == 210
    assert app_thread.mon.state.preview_window.cur_start_frame == 0
    assert app_thread.mon.state.preview_window.cur_end_frame == 210

    # new_img = pil_img_to_arr(pyautogui.screenshot(region=win_rect))
    # assert cmp_image(new_img, base_img) < 0.9, f'preview window screen is matching before and after loading video'

    state_dict = app_thread.mon.state.preview_window.as_dict()
    assert state_dict['video_path'] == video_path.str()
    assert round(state_dict['fps'], 2) == 29.97
    assert state_dict['total_frames'] == 210
    assert state_dict['frame_in_out']['in_frame'] == in_frame
    assert state_dict['frame_in_out']['out_frame'] == out_frame
    assert state_dict['current_frame_no'] == (current_frame_no or out_frame or in_frame)
    assert not state_dict['is_max_speed']
    assert state_dict['time_skip_multiplier'] == 1
    assert state_dict['cur_total_frames'] > 0
    assert state_dict['cur_start_frame'] == 0
    assert state_dict['cur_end_frame'] == 210


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
