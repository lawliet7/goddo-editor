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
from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.common_asserts import assert_state_is_blank
from goddo_test.utils.assert_utils import assert_blank_timeline, generic_assert, get_assert_blank_list_fn, get_assert_file_list_for_test_file_1_fn, get_assert_preview_for_blank_file_fn, get_assert_preview_for_test_file_1_fn
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.test_utils import drag_and_drop, save_reload_and_assert_state, wait_until, pil_img_to_arr, cmp_image
from goddo_test.utils.windows_container import WindowsContainer


def test_dbl_click_video_list(app_thread, windows_container: WindowsContainer, blank_state):
    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    file_path = video_folder_path().joinpath('supported').joinpath("test_vid.mp4").resolve()
    video_path = VideoPath(file_to_url(file_path))
    app_thread.cmd.submit_cmd(Command(CommandType.ADD_ITEM_DND_WINDOW, [video_path.str()]))

    dnd_widget = app_thread.cmd.dnd_widget

    item_idx = dnd_widget.get_count() - 1
    _, item_widget = dnd_widget.get_item_and_widget(item_idx)

    src_corner_pt = dnd_widget.item_widget_pos(item_idx)
    src_pt_x = src_corner_pt.x() + 10
    src_pt_y = src_corner_pt.y() + int(item_widget.size().height() / 2)

    videos_tab = windows_container.tabbed_list_window.videos_tab
    video_tab_list_widget = videos_tab.list_widget
    dest_corner_pt = local_to_global_pos(video_tab_list_widget, videos_tab)
    dest_pt_x = dest_corner_pt.x() + 10
    dest_pt_y = dest_corner_pt.y() + 10

    cur_file_count = video_tab_list_widget.count()

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    new_total_count_expected = cur_file_count + 1

    wait_until(lambda: video_tab_list_widget.count() == new_total_count_expected)
    wait_until(lambda: videos_tab.thread_pool.activeThreadCount() == 0)

    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    win_rect = windows_container.preview_window.geometry().getRect()
    base_img = pil_img_to_arr(pyautogui.screenshot(region=win_rect))

    item = video_tab_list_widget.get_all_items()[0]
    item_widget = video_tab_list_widget.itemWidget(item)
    pt = local_to_global_pos(item_widget, video_tab_list_widget)
    pyautogui.moveTo(pt.x() + 10, pt.y() + 10)
    pyautogui.doubleClick()

    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)

    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    # assert_state(app_thread, windows_container, video_path, 0.01, 0.15)
    # save_reload_and_assert_state(app_thread, windows_container, blank_state, 'test_drop_on_preview_window.json')
    generic_assert(app_thread, windows_container, blank_state, 'test_drop_on_preview_window.json',
                   get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), get_assert_preview_for_test_file_1_fn(0.01, 0.15), 
                   get_assert_preview_for_blank_file_fn(is_output_window=True), assert_blank_timeline)


def test_drop_on_preview_window(app_thread, windows_container: WindowsContainer, blank_state):
    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    file_path = video_folder_path().joinpath('supported').joinpath(f"test_vid.mp4").resolve()
    video_path = VideoPath(file_to_url(file_path))
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

    win_rect = windows_container.preview_window.geometry().getRect()
    base_img = pil_img_to_arr(pyautogui.screenshot(region=win_rect))

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)

    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    # assert_after_open(app_thread, windows_container, video_path, win_rect, base_img)
    assert_state(app_thread, windows_container, video_path, 0.01, 0.15)
    save_reload_and_assert_state(app_thread, windows_container, blank_state, 'test_drop_on_preview_window.json')
    # time.sleep(1)


def assert_after_open(app_thread, windows_container, video_path, win_rect, base_img):
    # asserts
    assert windows_container.preview_window.label.text() != 'you suck'

    # label should be like 0:00:0X.XX/0:00:07:00
    assert re.match('0:00:0[0-9]\\.[0-9]{2}/0:00:07\\.00', windows_container.preview_window.label.text()[:21])

    assert windows_container.preview_window.slider.value() > 0
    assert windows_container.preview_window.slider.isEnabled()
    assert windows_container.preview_window.windowTitle().endswith(f'- {video_path.file_name(include_ext=False)}')
    assert windows_container.preview_window.preview_widget.frame_pixmap
    assert windows_container.preview_window.preview_widget.get_cur_frame_no() > 0

    # asert everything inside state
    assert app_thread.mon.state.preview_window.name == 'source'
    assert app_thread.mon.state.preview_window.video_path == video_path
    assert round(app_thread.mon.state.preview_window.fps, 2) == 29.97
    assert app_thread.mon.state.preview_window.total_frames == 210
    assert app_thread.mon.state.preview_window.frame_in_out == FrameInOut()
    assert app_thread.mon.state.preview_window.current_frame_no > 0
    assert not app_thread.mon.state.preview_window.is_max_speed
    assert app_thread.mon.state.preview_window.time_skip_multiplier == 1
    assert app_thread.mon.state.preview_window.cur_total_frames > 0
    assert app_thread.mon.state.preview_window.cur_start_frame == 0
    assert app_thread.mon.state.preview_window.cur_end_frame == 210

    new_img = pil_img_to_arr(pyautogui.screenshot(region=win_rect))
    assert cmp_image(new_img, base_img) < 0.9, f'preview window screen is matching before and after loading video'

    state_dict = app_thread.mon.state.preview_window.as_dict()
    assert state_dict['video_path'] == video_path.str()
    assert round(state_dict['fps'], 2) == 29.97
    assert state_dict['total_frames'] == 210
    assert state_dict['frame_in_out']['in_frame'] is None
    assert state_dict['frame_in_out']['out_frame'] is None
    assert state_dict['current_frame_no'] > 0
    assert not state_dict['is_max_speed']
    assert state_dict['time_skip_multiplier'] == 1
    assert state_dict['cur_total_frames'] > 0
    assert state_dict['cur_start_frame'] == 0
    assert state_dict['cur_end_frame'] == 210

    file_list_state = app_thread.mon.state.file_list
    videos_tab = app_thread.mon.tabbed_list_window.videos_tab
    video_tab_list_widget = videos_tab.list_widget

    new_total_count_expected  = 1

    # assert on state
    assert len(file_list_state.files) == new_total_count_expected
    assert len(file_list_state.files_dict) == new_total_count_expected

    file_item = file_list_state.files[-1]
    assert file_item.name == video_path
    assert len(file_item.tags) == 0
    assert video_path.str() in file_list_state.files_dict
    assert file_list_state.files_dict[video_path.str()] == file_item

    # assert on widget
    assert video_tab_list_widget.count() == new_total_count_expected

    item = video_tab_list_widget.item(video_tab_list_widget.count() - 1)
    item_widget = video_tab_list_widget.itemWidget(item)
    item_label = item_widget.file_name_label.text()
    assert item_label == video_path.file_name()

    # wait for screenshot to finish loading
    wait_until(lambda: app_thread.cmd.queue_is_empty())

    pixmap = item_widget.screenshot_label.pixmap()
    assert pixmap != videos_tab.black_pixmap

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