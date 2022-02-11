import sys
import time
from unittest import mock

import numpy as np
import pytest
from PyQt5.QtCore import Qt, QPoint, QPointF, QMimeData, QUrl
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

from goddo_player.app.monarch import MonarchSystem
from goddo_player.utils.url_utils import get_file_name_from_url, file_to_url


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

    # qtbot.addWidget(file_window)
    # qtbot.addWidget(preview_window)
    # qtbot.addWidget(output_window)
    # qtbot.addWidget(timeline_window)
    #
    # qtbot.wait(2000)

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

def qimg_to_arr(img):
    num_of_channels = 4
    h = img.height()
    w = img.width()

    b = img.bits()
    b.setsize(h * w * num_of_channels)

    arr = np.frombuffer(b, np.uint8).reshape((h, w, num_of_channels))

    return arr

def cmp_image(img1, img2):
    import cv2
    res = cv2.matchTemplate(qimg_to_arr(img1), qimg_to_arr(img2), cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print('{}, {}, {}, {}'.format(min_val, max_val, min_loc, max_loc))
    return max_val

def grab_all_window_imgs(windows_tuple):
    screen = QApplication.primaryScreen()
    screen_img = screen.grabWindow(0).toImage()
    return [screen_img.copy(x.geometry()) for x in windows_tuple]

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
    url = file_to_url(r'C:\Users\William\dev\ayumi.mp4')
    file_name = get_file_name_from_url(url)

    mime_data = QMimeData()
    mime_data.setUrls([url])
    event = QDropEvent(QPoint(0,0), Qt.CopyAction, mime_data, Qt.LeftButton, Qt.NoModifier)

    file_list_state = file_window.state.file_list
    cur_num_of_items = len(file_list_state.files)
    expected_num_of_items = cur_num_of_items + 1

    # there's no support for drag and drop in pytest-qt so we have to fake this
    file_window.listWidget.dropEvent(event)

    file_item = file_list_state.files[-1]
    assert len(file_list_state.files) == expected_num_of_items
    assert len(file_list_state.files_dict) == expected_num_of_items
    assert file_item.name == url
    assert len(file_item.tags) == 0
    assert url.path() in file_list_state.files_dict
    assert file_list_state.files_dict[url.path()] == file_item

    assert file_window.listWidget.count() == expected_num_of_items

    items = file_window.listWidget.get_all_items()
    for item in items:
        item_widget = file_window.listWidget.itemWidget(item)
        name = item_widget.findChildren(QLabel, "name")[0].text()
        if file_name == name:
            file_item2 = item_widget
            break

    assert file_item2

    # wait for screenshot to finish loading
    def check_no_more_threads_running():
        assert file_window.thread_pool.activeThreadCount() == 0

    qtbot.waitUntil(check_no_more_threads_running, timeout=10000)

    screenshot_label = item_widget.findChildren(QLabel, "screenshot")[0]
    pixmap = screenshot_label.pixmap()
    assert pixmap != file_window.black_pixmap

