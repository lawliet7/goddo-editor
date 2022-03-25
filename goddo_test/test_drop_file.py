import logging
import time

import pytest
from PyQt5.QtWidgets import QLabel

from goddo_player.utils.video_path import VideoPath
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.common_asserts import assert_state_is_blank
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.test_utils import wait_until, drag_and_drop


def get_list_of_test_file_exts():
    path = video_folder_path().joinpath('supported').resolve()
    return [file_path.suffix[1:] for file_path in path.iterdir()]


FILE_EXT_PARAMS = get_list_of_test_file_exts()


@pytest.mark.parametrize("test_file_ext", FILE_EXT_PARAMS)
def test_drop_vid_file(app_thread, windows_container, test_file_ext):
    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    file_path = video_folder_path().joinpath('supported').joinpath(f"test_vid.{test_file_ext}").resolve()
    video_path = VideoPath(file_to_url(file_path))
    app_thread.cmd.submit_cmd(Command(CommandType.ADD_ITEM_DND_WINDOW, [video_path.str()]))

    dnd_widget = app_thread.cmd.dnd_widget

    item_idx = dnd_widget.get_count() - 1
    _, item_widget = dnd_widget.get_item_and_widget(item_idx)

    src_corner_pt = dnd_widget.item_widget_pos(item_idx)
    src_pt_x = src_corner_pt.x() + 10
    src_pt_y = src_corner_pt.y() + int(item_widget.size().height() / 2)

    videos_tab = windows_container.tabbed_list_window.videos_tab
    video_tab_list_widget = videos_tab.listWidget
    dest_corner_pt = local_to_global_pos(video_tab_list_widget, videos_tab)
    dest_pt_x = dest_corner_pt.x() + 10
    dest_pt_y = dest_corner_pt.y() + 10

    cur_file_count = video_tab_list_widget.count()

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    new_total_count_expected = cur_file_count+1

    wait_until(lambda: video_tab_list_widget.count() == new_total_count_expected)
    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.thread_pool.activeThreadCount() == 0)

    assert_after_drop(app_thread, video_path, new_total_count_expected)

    save_file_path = my_test_output_folder_path().joinpath(f'drop_{test_file_ext}_save.json').resolve()
    app_thread.cmd.submit_cmd(Command(CommandType.SAVE_FILE, [VideoPath(file_to_url(str(save_file_path)))]))

    app_thread.cmd.submit_cmd(Command(CommandType.RESET))

    assert_state_is_blank(app_thread, windows_container)

    app_thread.cmd.submit_cmd(Command(CommandType.LOAD_FILE, [VideoPath(file_to_url(str(save_file_path)))]))

    assert_after_drop(app_thread, video_path, new_total_count_expected)



def test_drop_multiple_vid_file(app_thread, windows_container):
    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    file_path1 = video_folder_path().joinpath('supported').joinpath(f"test_vid.mp4").resolve()
    video_path1 = VideoPath(file_to_url(file_path1))
    app_thread.cmd.submit_cmd(Command(CommandType.ADD_ITEM_DND_WINDOW, [video_path1.str()]))

    file_path2 = video_folder_path().joinpath(f"test_vid2.mp4").resolve()
    video_path2 = VideoPath(file_to_url(file_path2))
    app_thread.cmd.submit_cmd(Command(CommandType.ADD_ITEM_DND_WINDOW, [video_path2.str()]))

    dnd_widget = app_thread.cmd.dnd_widget

    _, item_widget = dnd_widget.get_item_and_widget(0)

    src_corner_pt = dnd_widget.item_widget_pos(0)
    src_pt_x = src_corner_pt.x() + 10
    src_pt_y = src_corner_pt.y() + int(item_widget.size().height() / 2)

    videos_tab = windows_container.tabbed_list_window.videos_tab
    video_tab_list_widget = videos_tab.listWidget
    dest_corner_pt = local_to_global_pos(video_tab_list_widget, videos_tab)
    dest_pt_x = dest_corner_pt.x() + 10
    dest_pt_y = dest_corner_pt.y() + 10

    cur_file_count = video_tab_list_widget.count()

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    new_total_count_expected = cur_file_count+2

    wait_until(lambda: video_tab_list_widget.count() == new_total_count_expected)
    wait_until(lambda: app_thread.mon.tabbed_list_window.videos_tab.thread_pool.activeThreadCount() == 0)

    assert_after_multiple_drop(app_thread, video_path1, video_path2, new_total_count_expected)

    save_file_path = my_test_output_folder_path().joinpath(f'drop_multiple_save.json').resolve()
    app_thread.cmd.submit_cmd(Command(CommandType.SAVE_FILE, [VideoPath(file_to_url(str(save_file_path)))]))

    app_thread.cmd.submit_cmd(Command(CommandType.RESET))

    assert_state_is_blank(app_thread, windows_container)

    app_thread.cmd.submit_cmd(Command(CommandType.LOAD_FILE, [VideoPath(file_to_url(str(save_file_path)))]))

    assert_after_multiple_drop(app_thread, video_path1, video_path2, new_total_count_expected)


def assert_after_drop(app_thread, video_path, new_total_count_expected):
    file_list_state = app_thread.mon.state.file_list
    videos_tab = app_thread.mon.tabbed_list_window.videos_tab
    video_tab_list_widget = videos_tab.listWidget

    # assert on state
    logging.info(f'{len(file_list_state.files)} - {new_total_count_expected}')
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
    item_label = item_widget.findChildren(QLabel, "name")[0].text()
    assert item_label == video_path.file_name()

    # wait for screenshot to finish loading
    wait_until(lambda: app_thread.cmd.queue_is_empty())

    screenshot_label = item_widget.findChildren(QLabel, "screenshot")[0]
    pixmap = screenshot_label.pixmap()
    assert pixmap != videos_tab.black_pixmap


def assert_after_multiple_drop(app_thread, video_path1, video_path2, new_total_count_expected):
    file_list_state = app_thread.mon.state.file_list
    videos_tab = app_thread.mon.tabbed_list_window.videos_tab
    video_tab_list_widget = videos_tab.listWidget

    # assert on state
    logging.info(f'{len(file_list_state.files)} - {new_total_count_expected}')
    assert len(file_list_state.files) == new_total_count_expected
    assert len(file_list_state.files_dict) == new_total_count_expected

    file_item = file_list_state.files[-2]
    assert file_item.name == video_path1
    assert len(file_item.tags) == 0
    assert video_path1.str() in file_list_state.files_dict
    assert file_list_state.files_dict[video_path1.str()] == file_item

    file_item = file_list_state.files[-1]
    assert file_item.name == video_path2
    assert len(file_item.tags) == 0
    assert video_path2.str() in file_list_state.files_dict
    assert file_list_state.files_dict[video_path2.str()] == file_item

    # assert on widget
    assert video_tab_list_widget.count() == new_total_count_expected

    item = video_tab_list_widget.item(video_tab_list_widget.count() - 2)
    item_widget = video_tab_list_widget.itemWidget(item)
    item_label = item_widget.findChildren(QLabel, "name")[0].text()
    assert item_label == video_path1.file_name()

    item = video_tab_list_widget.item(video_tab_list_widget.count() - 1)
    item_widget = video_tab_list_widget.itemWidget(item)
    item_label = item_widget.findChildren(QLabel, "name")[0].text()
    assert item_label == video_path2.file_name()

    # wait for screenshot to finish loading
    wait_until(lambda: app_thread.cmd.queue_is_empty())

    screenshot_label = item_widget.findChildren(QLabel, "screenshot")[0]
    pixmap = screenshot_label.pixmap()
    assert pixmap != videos_tab.black_pixmap
