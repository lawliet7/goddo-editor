import logging
import time

import pytest
from PyQt5.QtWidgets import QLabel

from goddo_player.utils.video_path import VideoPath
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.common_asserts import assert_state_is_blank
from goddo_test.utils.assert_utils import *
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.test_utils import drop_video_on_file_list, get_test_vid_2_path, get_test_vid_path, wait_until, drag_and_drop


def get_list_of_test_file_exts():
    path = video_folder_path().joinpath('supported').resolve()
    return [file_path.suffix[1:] for file_path in path.iterdir()]


FILE_EXT_PARAMS = get_list_of_test_file_exts()

@pytest.mark.parametrize("test_file_ext", FILE_EXT_PARAMS)
def test_drop_vid_file(app_thread, windows_container, blank_state, test_file_ext):
    video_path = get_test_vid_path(test_file_ext)
    drop_video_on_file_list(app_thread, windows_container, [video_path])

    new_total_count_expected = 1

    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.list_widget.count() == new_total_count_expected)
    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.thread_pool.activeThreadCount() == 0)

    generic_assert(app_thread, windows_container, blank_state,
                get_assert_file_list_for_test_file_1_fn(ext=test_file_ext), get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline,
                save_file=f'<file_name>.<method_name>_{test_file_ext}.json')



def test_drop_multiple_vid_file(app_thread, windows_container, blank_state):
    video_path1 = get_test_vid_path()
    video_path2 = get_test_vid_2_path()
    drop_video_on_file_list(app_thread, windows_container, [video_path1, video_path2])

    new_total_count_expected = 2

    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.list_widget.count() == new_total_count_expected)
    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.thread_pool.activeThreadCount() == 0)

    generic_assert(app_thread, windows_container, blank_state,
                assert_file_list_for_multiple_files, get_assert_blank_list_fn(is_file_list=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=False), 
                get_assert_preview_for_blank_file_fn(is_output_window=True), 
                assert_blank_timeline)

def assert_file_list_for_multiple_files(app_thread, windows_container, state_dict, win_state_dict):
    video_path1 = get_test_vid_path()
    video_path2 = get_test_vid_2_path()

    assert state_dict['file_list']['files'][0]['name'] == str(video_path1)
    assert state_dict['file_list']['files'][0]['tags'] == []
    assert state_dict['file_list']['files'][1]['name'] == str(video_path2)
    assert state_dict['file_list']['files'][1]['tags'] == []

    assert state_dict['file_list']['files_dict'][str(video_path1)]['name'] == str(video_path1)
    assert state_dict['file_list']['files_dict'][str(video_path1)]['tags'] == []
    assert state_dict['file_list']['files_dict'][str(video_path2)]['name'] == str(video_path2)
    assert state_dict['file_list']['files_dict'][str(video_path2)]['tags'] == []

    # assert win state
    assert win_state_dict['tabbed_list_window']['geometry']['x'] == 0
    assert win_state_dict['tabbed_list_window']['geometry']['y'] == 27
    assert win_state_dict['tabbed_list_window']['geometry']['width'] == 546
    assert win_state_dict['tabbed_list_window']['geometry']['height'] == 1000

    clips = win_state_dict['tabbed_list_window']['videos_tab']['clips']
    assert len(clips) == 2

    assert clips[0]['name'] == video_path1.file_name()
    assert clips[0]['tags'] == []
    assert clips[1]['name'] == video_path2.file_name()
    assert clips[1]['tags'] == []

    # wait for screenshot to finish loading
    wait_until(lambda: app_thread.cmd.queue_is_empty())
    videos_tab = windows_container.tabbed_list_window.videos_tab
    video_tab_list_widget = videos_tab.list_widget

    item_widget1 = video_tab_list_widget.itemWidget(video_tab_list_widget.item(0))
    pixmap = item_widget1.screenshot_label.pixmap()
    assert pixmap != videos_tab.black_pixmap

    item_widget2 = video_tab_list_widget.itemWidget(video_tab_list_widget.item(1))
    pixmap = item_widget2.screenshot_label.pixmap()
    assert pixmap != videos_tab.black_pixmap
