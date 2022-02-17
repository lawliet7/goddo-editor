import sys
import time
from unittest import mock

import pyautogui
import pytest
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QListWidgetItem

from goddo_player.app.monarch import MonarchSystem
from goddo_player.utils.url_utils import file_to_url
from goddo_test.path_util import *
from goddo_test.test_utils import *


@pytest.fixture(scope='module')
def app():
    return QApplication(sys.argv)


@pytest.fixture(scope='module')
def monarch(app):
    return MonarchSystem(app)

@pytest.fixture(scope='module')
def file_window(monarch):
    return monarch.file_list_window

@pytest.fixture(scope='module')
def preview_window(monarch):
    return monarch.preview_window

@pytest.fixture(scope='module')
def output_window(monarch):
    return monarch.preview_window_output

@pytest.fixture(scope='module')
def timeline_window(monarch):
    return monarch.timeline_window

@pytest.mark.order(1)
def test_all_visible(qtbot, file_window, preview_window, output_window, timeline_window):

    assert file_window.isVisible()
    assert preview_window.isVisible()
    assert output_window.isVisible()
    assert timeline_window.isVisible()

@pytest.mark.order(2)
def test_quit_with_escape_btn(qtbot, file_window, preview_window, output_window, timeline_window):
    with mock.patch.object(QApplication, "exit"):
        qtbot.keyPress(file_window, Qt.Key_Escape)
        assert QApplication.exit.call_count == 1

        qtbot.keyPress(preview_window, Qt.Key_Escape)
        assert QApplication.exit.call_count == 2

        qtbot.keyPress(output_window, Qt.Key_Escape)
        assert QApplication.exit.call_count == 3

        qtbot.keyPress(timeline_window, Qt.Key_Escape)
        assert QApplication.exit.call_count == 4

def base_test_F2(qtbot, windows_tuple, idx, comparison_threshold=0.9):
    img_base_windows = grab_all_window_imgs(windows_tuple)

    w = QWidget()
    w.showMaximized()
    w.show()
    qtbot.waitExposed(w)

    windows_tuple[idx].activateWindow()

    # test can fail if activate window isn't fast enough
    time.sleep(0.2)

    img_new_windows = grab_all_window_imgs(windows_tuple)

    for i in range(len(windows_tuple)):
        if i == idx:
            assert cmp_image(img_new_windows[i], img_base_windows[i]) > comparison_threshold
        else:
            assert cmp_image(img_new_windows[i], img_base_windows[i]) < comparison_threshold

    qtbot.keyPress(windows_tuple[idx], Qt.Key_F2)

    img_new_windows = grab_all_window_imgs(windows_tuple)

    for i in range(len(windows_tuple)):
        assert cmp_image(img_new_windows[i], img_base_windows[i]) > comparison_threshold

    w.close()

@pytest.mark.order(2)
def test_file_window_show_all_win_with_F2(qtbot, file_window, preview_window, output_window, timeline_window):
    base_test_F2(qtbot, (file_window, preview_window, output_window, timeline_window), 0)

@pytest.mark.order(2)
def test_preview_window_show_all_win_with_F2(qtbot, file_window, preview_window, output_window, timeline_window):
    base_test_F2(qtbot, (file_window, preview_window, output_window, timeline_window), 1)

@pytest.mark.order(2)
def test_output_window_show_all_win_with_F2(qtbot, file_window, preview_window, output_window, timeline_window):
    base_test_F2(qtbot, (file_window, preview_window, output_window, timeline_window), 2)

@pytest.mark.order(2)
def test_timeline_window_show_all_win_with_F2(qtbot, file_window, preview_window, output_window, timeline_window):
    base_test_F2(qtbot, (file_window, preview_window, output_window, timeline_window), 3)

def base_test_minimized_F2(qtbot, windows_tuple, idx, comparison_threshold=0.9):
    img_base_windows = grab_all_window_imgs(windows_tuple)

    for i in range(len(windows_tuple)):
        if idx != i:
            windows_tuple[idx].showMinimized()

    # test can fail if restoring window isn't fast enough
    time.sleep(0.2)

    img_new_windows = grab_all_window_imgs(windows_tuple)

    for i in range(len(windows_tuple)):
        if i == idx:
            assert cmp_image(img_new_windows[i], img_base_windows[i]) > comparison_threshold
        else:
            assert cmp_image(img_new_windows[i], img_base_windows[i]) < comparison_threshold

    qtbot.keyPress(windows_tuple[idx], Qt.Key_F2)

    img_new_windows = grab_all_window_imgs(windows_tuple)

    for i in range(len(windows_tuple)):
        assert cmp_image(img_new_windows[i], img_base_windows[i]) > comparison_threshold

@pytest.mark.order(2)
def test_file_window_minimize_and_restore_win_with_F2(qtbot, file_window, preview_window, output_window, timeline_window):
    base_test_F2(qtbot, (file_window, preview_window, output_window, timeline_window), 0)

@pytest.mark.order(2)
def test_preview_window_minimize_and_restore_win_with_F2(qtbot, file_window, preview_window, output_window, timeline_window):
    base_test_F2(qtbot, (file_window, preview_window, output_window, timeline_window), 1)

@pytest.mark.order(2)
def test_output_window_minimize_and_restore_win_with_F2(qtbot, file_window, preview_window, output_window, timeline_window):
    base_test_F2(qtbot, (file_window, preview_window, output_window, timeline_window), 2)

@pytest.mark.order(2)
def test_timeline_window_minimize_and_restore_win_with_F2(qtbot, file_window, preview_window, output_window, timeline_window):
    base_test_F2(qtbot, (file_window, preview_window, output_window, timeline_window), 3)

@pytest.mark.order(3)
def test_drop_video_into_file_window(qtbot, file_window, preview_window, output_window, timeline_window):
    file_list_state = file_window.state.file_list
    cur_num_of_items = len(file_list_state.files)

    path = supported_video_folder_path().resolve()

    list_widget = list_widget_to_test_drag_and_drop()
    list_widget.show()
    qtbot.addWidget(list_widget)
    qtbot.waitExposed(list_widget)

    # ffmpeg -i test_vid.mp4 -q:v 0 -q:a 0 test_vid.mpg

    for file_path in path.iterdir():
        file_path_str = str(file_path)
        print(file_path.name)

        item = QListWidgetItem(list_widget)
        item_widget = QLabel(file_path_str)
        list_widget.setItemWidget(item, item_widget)

        if list_widget.count() > 1:
            def check_item_widget_y_not_0():
                assert item_widget.pos().y() != 0
            qtbot.waitUntil(check_item_widget_y_not_0)

        top_left_corner_pt1 = file_window.listWidget.mapToGlobal(file_window.listWidget.pos())
        # item_widget = list_widget.itemWidget(list_widget.item(list_widget.count() - 1))
        top_left_corner_pt2 = list_widget.mapToGlobal(item_widget.pos())

        # gui doesn't update with drop item without waiting
        qtbot.wait(1)

        pyautogui.mouseDown(top_left_corner_pt2.x() + 10, top_left_corner_pt2.y() + 5, duration=1)
        pyautogui.dragTo(top_left_corner_pt1.x() + 100, top_left_corner_pt1.y() + 50, duration=1)
        pyautogui.mouseUp()

        # gui doesn't update with drop item without waiting
        qtbot.wait(1)

        # wait for screenshot to finish loading
        wait_for_threadpool_to_complete(qtbot, file_window.thread_pool)

        screenshot_file_name = f"drop-screenshot-{file_path.name[:file_path.name.find('.')]}.png"
        save_screenshot(screenshot_file_name)

        # https://www.youtube.com/watch?v=EKVwYkhOTeo

        expected_num_of_items = cur_num_of_items + 1

        file_path_url = file_to_url(file_path_str)

        # assert on state
        file_item = file_list_state.files[-1]
        assert len(file_list_state.files) == expected_num_of_items
        assert len(file_list_state.files_dict) == expected_num_of_items
        assert file_item.name == file_path_url
        assert len(file_item.tags) == 0
        assert file_path_url.path() in file_list_state.files_dict
        assert file_list_state.files_dict[file_path_url.path()] == file_item

        # assert on widget
        assert file_window.listWidget.count() == expected_num_of_items

        item = file_window.listWidget.item(file_window.listWidget.count() - 1)
        item_widget = file_window.listWidget.itemWidget(item)
        item_label = item_widget.findChildren(QLabel, "name")[0].text()
        assert item_label == file_path_url.fileName()

        # wait for screenshot to finish loading
        wait_for_threadpool_to_complete(qtbot, file_window.thread_pool)

        screenshot_label = item_widget.findChildren(QLabel, "screenshot")[0]
        pixmap = screenshot_label.pixmap()
        assert pixmap != file_window.black_pixmap

        cur_num_of_items = file_window.listWidget.count()
