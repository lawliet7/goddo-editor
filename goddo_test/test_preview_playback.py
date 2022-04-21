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

    assert_state(app_thread, windows_container, video_path, 0.89, 1)
    save_reload_and_assert_state(app_thread, windows_container, blank_state, 'test_out_frame_save.json')

def test_while_paused_seek_on_slider(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    img_base = pil_img_to_arr(pyautogui.screenshot())

    click_on_prev_wind_slider(windows_container.preview_window, 0.9)
    time.sleep(0.5)

    logging.info(f'slider value {windows_container.preview_window.slider.value()}')
    img_new = pil_img_to_arr(pyautogui.screenshot())

    assert cmp_image(img_base, img_new) < 0.98

    _, _, secs, frames = time_str_to_components(windows_container.preview_window.label.text()[:10])
    assert secs == 6
    assert 5 <= frames <= 15

    assert_state(app_thread, windows_container, video_path, 0.89, 0.91)
    save_reload_and_assert_state(app_thread, windows_container, blank_state, 'test_while_paused_seek_on_slider.json')

def assert_state(app_thread, windows_container, video_path, slider_start_pct, slider_end_pct):
    state_dict = app_thread.mon.state.as_dict()
    logging.info(f'state dict {state_dict}')

    video_total_frames = 210
    fps_2_places = 29.97

    # preview window asserts
    assert state_dict['preview_window']['video_path'] == str(video_path)
    assert round(state_dict['preview_window']['fps'],2) == fps_2_places
    assert state_dict['preview_window']['total_frames'] == video_total_frames
    assert state_dict['preview_window']['frame_in_out']['in_frame'] is None
    assert state_dict['preview_window']['frame_in_out']['out_frame'] is None
    assert int(video_total_frames * slider_start_pct) <= state_dict['preview_window']['current_frame_no'] <= int(video_total_frames * slider_end_pct)
    assert not state_dict['preview_window']['is_max_speed']
    assert state_dict['preview_window']['time_skip_multiplier'] == 1
    assert state_dict['preview_window']['cur_total_frames'] == video_total_frames
    assert state_dict['preview_window']['cur_start_frame'] == 0
    assert state_dict['preview_window']['cur_end_frame'] == video_total_frames

    # preview window output asserts
    assert state_dict['preview_window_output']['video_path'] == ''
    assert state_dict['preview_window_output']['fps'] == 0
    assert state_dict['preview_window_output']['total_frames'] == 0
    assert state_dict['preview_window_output']['frame_in_out']['in_frame'] is None
    assert state_dict['preview_window_output']['frame_in_out']['out_frame'] is None
    assert state_dict['preview_window_output']['current_frame_no'] == 0
    assert not state_dict['preview_window_output']['is_max_speed']
    assert state_dict['preview_window_output']['time_skip_multiplier'] == 1
    assert state_dict['preview_window_output']['cur_total_frames'] == 0
    assert state_dict['preview_window_output']['cur_start_frame'] == 0
    assert state_dict['preview_window_output']['cur_end_frame'] == 0

    assert state_dict['app_config']['extra_frames_in_secs_config'] == 10

    def assert_file_item(file_item_dict):
        assert file_item_dict['name'] == str(video_path)
        assert file_item_dict['tags'] == []

    for f in state_dict['file_list']['files']:
        assert_file_item(f)

    for k,v in state_dict['file_list']['files_dict'].items():
        assert k == str(video_path)
        assert_file_item(v)

    # todo clip list not implemented yet
    assert len(state_dict['clip_list']['clips']) == 0
    assert len(state_dict['clip_list']['clips_dict']) == 0

    # assert timeline
    assert len(state_dict['timeline']['clips']) == 0
    # for c in state_dict['timeline']['clips']:
    #     assert c['video_path'] == str(video_path)
    #     assert round(c['fps'],2) == 29.97
    #     assert c['total_frames'] == str(video_path)
    #     assert c['frame_in_out']['in_frame'] == str(video_path)
    #     assert c['frame_in_out']['out_frame'] == str(video_path)
    assert state_dict['timeline']['width_of_one_min'] == 120
    assert state_dict['timeline']['selected_clip_index'] == -1
    assert state_dict['timeline']['opened_clip_index'] == -1

    win_state_dict = windows_container.as_dict()

    # assert window preview
    assert win_state_dict['tabbed_list_window']['geometry']['x'] == 0
    assert win_state_dict['tabbed_list_window']['geometry']['y'] == 27
    assert win_state_dict['tabbed_list_window']['geometry']['width'] == 546
    assert win_state_dict['tabbed_list_window']['geometry']['height'] == 1000

    for c in win_state_dict['tabbed_list_window']['videos_tab']['clips']:
        assert c['name'] == video_path.file_name()
        assert c['tags'] == []

    # todo clip list not implemented yet
    assert len(win_state_dict['tabbed_list_window']['clips_tab']['clips']) == 0

    # assert win state preview window
    assert win_state_dict['preview_window']['windowTitle'].endswith(f' - {video_path.file_name(include_ext=False)}')
    assert win_state_dict['preview_window']['geometry']['x'] == 546
    assert win_state_dict['preview_window']['geometry']['y'] == 78
    assert win_state_dict['preview_window']['geometry']['width'] == 640
    assert win_state_dict['preview_window']['geometry']['height'] == 407
    logging.info(win_state_dict['preview_window']['label'])

    time_label, speed_label, skip_label = [x for x in win_state_dict['preview_window']['label'].split(' ') if x.strip() != '']
    assert speed_label.strip() == 'speed=normal'
    assert skip_label.strip() == 'skip=5s'

    cur_time_label, total_time_label = time_label.split('/')
    assert total_time_label.strip() == '0:00:07.00'

    total_frames_in_time_label = time_str_to_frames(cur_time_label,fps_2_places)
    assert int(video_total_frames * slider_start_pct) <= total_frames_in_time_label <= int(video_total_frames * slider_end_pct)

    slider_max = windows_container.preview_window.slider.maximum()
    assert win_state_dict['preview_window']['slider']['isEnabled'] == True
    assert slider_max * slider_start_pct <= win_state_dict['preview_window']['slider']['value'] <= slider_max * slider_end_pct
    assert win_state_dict['preview_window']['restrict_frame_interval'] == False

    # assert win state output
    assert ' - clip#' not in win_state_dict['output_window']['windowTitle']
    assert win_state_dict['output_window']['geometry']['x'] == 1196
    assert win_state_dict['output_window']['geometry']['y'] == 78
    assert win_state_dict['output_window']['geometry']['width'] == 640
    assert win_state_dict['output_window']['geometry']['height'] == 407
    assert win_state_dict['output_window']['label'] == 'you suck'
    assert win_state_dict['output_window']['slider']['isEnabled'] == False
    assert win_state_dict['output_window']['slider']['value'] == 0
    assert win_state_dict['output_window']['restrict_frame_interval'] == True

     # assert win state timeline
    assert win_state_dict['timeline_window']['geometry']['x'] == 546
    assert win_state_dict['timeline_window']['geometry']['y'] == 525
    assert win_state_dict['timeline_window']['geometry']['width'] == 1075
    assert win_state_dict['timeline_window']['geometry']['height'] == 393
    assert win_state_dict['timeline_window']['innerWidgetSize']['width'] == 1075
    assert win_state_dict['timeline_window']['innerWidgetSize']['height'] == 393
    assert len(win_state_dict['timeline_window']['clip_rects']) == 0


    '''
  "timeline_window": {
    "windowTitle": "美少女捜査官",
    "geometry": {
      "x": 0,
      "y": 27,
      "width": 546,
      "height": 1000
    },
    "innerWidgetSize": {
      "height": 393,
      "width": 1075
    },
    "clip_rects": [
      [
        {
          "video_path": "...",
          "fps": 29.97002997002997,
          "total_frames": 75879,
          "frame_in_out": {
            "in_frame": 1545,
            "out_frame": 3424
          }
        },
        {
          "x": 0,
          "y": 68,
          "width": 125,
          "height": 100
        }
      ]
    ]
  }
}
    '''

    
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
