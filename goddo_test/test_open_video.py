import time

import pyautogui

from goddo_player.app.video_path import VideoPath
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.window_util import local_to_global_pos
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path
from goddo_test.utils.test_utils import drag_and_drop, wait_until
from goddo_test.utils.windows_container import WindowsContainer


def test_dbl_click_video_list(app_thread, windows_container: WindowsContainer):
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

    videos_tab = windows_container.tabbed_list_window.videos_tab
    video_tab_list_widget = videos_tab.listWidget
    dest_corner_pt = local_to_global_pos(video_tab_list_widget.pos(), videos_tab)
    dest_pt_x = dest_corner_pt.x() + 10
    dest_pt_y = dest_corner_pt.y() + 10

    cur_file_count = video_tab_list_widget.count()

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    new_total_count_expected = cur_file_count + 1

    wait_until(lambda: video_tab_list_widget.count() == new_total_count_expected)
    wait_until(lambda: videos_tab.thread_pool.activeThreadCount() == 0)

    app_thread.cmd.submit_cmd(Command(CommandType.HIDE_DND_WINDOW))

    item = video_tab_list_widget.get_all_items()[0]
    item_widget = video_tab_list_widget.itemWidget(item)
    pt = local_to_global_pos(item_widget, video_tab_list_widget)
    pyautogui.moveTo(pt.x() + 10, pt.y() + 10)
    pyautogui.doubleClick()

    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)

    app_thread.cmd.submit_cmd(Command(CommandType.PAUSE_PREVIEW_VIDEO))

    # asserts
    assert windows_container.preview_window.label != 'you suck'

    # time.sleep(2)
