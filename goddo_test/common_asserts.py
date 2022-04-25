from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.video_path import VideoPath

from PyQt5.QtCore import QUrl


def assert_state_is_blank(app_thread, windows_container):

    file_list_state = app_thread.mon.state.file_list
    videos_tab = app_thread.mon.tabbed_list_window.videos_tab
    video_tab_list_widget = videos_tab.list_widget
    assert len(file_list_state.files) == 0
    assert len(file_list_state.files_dict) == 0
    assert video_tab_list_widget.count() == 0

    # asserts
    assert windows_container.preview_window.label.text() == 'you suck'

    assert windows_container.preview_window.slider.value() == 0
    assert not windows_container.preview_window.slider.isEnabled()
    assert ' - ' not in windows_container.preview_window.windowTitle()
    assert windows_container.preview_window.preview_widget.frame_pixmap is None
    assert windows_container.preview_window.preview_widget.get_cur_frame_no() == 0

    # asert everything inside state
    assert app_thread.mon.state.preview_window.name == 'source'
    assert app_thread.mon.state.preview_window.video_path == VideoPath(QUrl(''))
    assert app_thread.mon.state.preview_window.fps == 0
    assert app_thread.mon.state.preview_window.total_frames == 0
    assert app_thread.mon.state.preview_window.frame_in_out == FrameInOut()
    assert app_thread.mon.state.preview_window.current_frame_no == 0
    assert not app_thread.mon.state.preview_window.is_max_speed
    assert app_thread.mon.state.preview_window.time_skip_multiplier == 1
    assert app_thread.mon.state.preview_window.cur_total_frames == 0
    assert app_thread.mon.state.preview_window.cur_start_frame == 0
    assert app_thread.mon.state.preview_window.cur_end_frame == 0

    # new_img = pil_img_to_arr(pyautogui.screenshot(region=win_rect))
    # assert cmp_image(new_img, base_img) < 0.9, f'preview window screen is matching before and after loading video'

    state_dict = app_thread.mon.state.preview_window.as_dict()
    assert state_dict['video_path'] == ''
    assert state_dict['fps'] == 0
    assert state_dict['total_frames'] == 0
    assert state_dict['frame_in_out']['in_frame'] is None
    assert state_dict['frame_in_out']['out_frame'] is None
    assert state_dict['current_frame_no'] == 0
    assert not state_dict['is_max_speed']
    assert state_dict['time_skip_multiplier'] == 1
    assert state_dict['cur_total_frames'] == 0
    assert state_dict['cur_start_frame'] == 0
    assert state_dict['cur_end_frame'] == 0
