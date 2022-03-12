import time

import pyautogui

from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path
from goddo_test.utils.test_utils import wait_until, drag_and_drop


def test_drop_vid_file(app_thread, windows_dict):
    app_thread.cmd.submit_cmd(Command(CommandType.SHOW_DND_WINDOW))

    path = video_folder_path().joinpath('supported').resolve()
    for file_path in path.iterdir():
        app_thread.cmd.submit_cmd(Command(CommandType.ADD_ITEM_DND_WINDOW, [str(file_path)]))
        break

    wait_until(lambda: app_thread.cmd.queue_is_empty())

    item_idx = app_thread.cmd.dnd_widget.get_count() - 1
    _, item_widget = app_thread.cmd.dnd_widget.get_item_and_widget(item_idx)

    src_corner_pt = app_thread.cmd.dnd_widget.item_widget_pos(item_idx)
    src_pt_x = src_corner_pt.x() + 10
    src_pt_y = src_corner_pt.y() + int(item_widget.size().height() / 2)

    w = windows_dict['TABBED_LIST_WINDOW']
    dest_corner_pt = w.videos_tab.mapToGlobal(w.videos_tab.listWidget.pos())
    dest_pt_x = dest_corner_pt.x() + 10
    dest_pt_y = dest_corner_pt.y() + 10

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    print('you got it')
    time.sleep(1)

    # wait until list widget has 1 more item and the threadpool has no more tasks

    # file_list_state = file_list_window.state.file_list
    #
    #
    # # assert on state
    # print(f'{len(file_list_state.files)} - {new_total_count_expected}')
    # assert len(file_list_state.files) == new_total_count_expected
    # assert len(file_list_state.files_dict) == new_total_count_expected
    #
    # file_item = file_list_state.files[-1]
    # assert file_item.name == new_file_url_added
    # assert len(file_item.tags) == 0
    # assert new_file_url_added.path() in file_list_state.files_dict
    # assert file_list_state.files_dict[new_file_url_added.path()] == file_item
    #
    # # assert on widget
    # assert file_list_window.listWidget.count() == new_total_count_expected
    #
    # item = file_list_window.listWidget.item(file_list_window.listWidget.count() - 1)
    # item_widget = file_list_window.listWidget.itemWidget(item)
    # item_label = item_widget.findChildren(QLabel, "name")[0].text()
    # assert item_label == new_file_url_added.fileName()
    #
    # # wait for screenshot to finish loading
    # wait_for_threadpool_to_complete(qtbot, file_list_window.thread_pool)
    #
    # screenshot_label = item_widget.findChildren(QLabel, "screenshot")[0]
    # pixmap = screenshot_label.pixmap()
    # assert pixmap != file_list_window.black_pixmap
