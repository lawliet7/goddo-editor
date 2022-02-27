# import sys
#
# import pyautogui
# import pytest
# from PyQt5.QtCore import Qt, QTimer
# from PyQt5.QtWidgets import QLabel, QListWidgetItem, QMessageBox
#
# from goddo_player.app.monarch import MonarchSystem
# from goddo_test.utils.path_util import *
# from goddo_test.utils.test_utils import *
#
#
# @pytest.fixture(scope='module')
# def app():
#     return QApplication(sys.argv)
#
#
# @pytest.fixture(scope='module')
# def monarch(app):
#     return MonarchSystem(app)
#
#
# @pytest.fixture(scope='module')
# def tabbed_list_window(monarch):
#     return monarch.tabbed_list_window
#
#
# @pytest.fixture(scope='module')
# def preview_window(monarch):
#     return monarch.preview_window
#
#
# @pytest.fixture(scope='module')
# def output_window(monarch):
#     return monarch.preview_window_output
#
#
# @pytest.fixture(scope='module')
# def timeline_window(monarch):
#     return monarch.timeline_window
#
#
# @pytest.mark.order(3)
# def test_drop_supported_video_into_file_window(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     file_list_state = tabbed_list_window.state.file_list
#     cur_num_of_items = len(file_list_state.files)
#
#     list_widget = list_widget_to_test_drag_and_drop()
#     qtbot.addWidget(list_widget)
#     qtbot.waitExposed(list_widget)
#
#     # ffmpeg -i test_vid.mp4 -q:v 0 -q:a 0 test_vid.mpg
#
#     path = video_folder_path().joinpath('supported').resolve()
#     for file_path in path.iterdir():
#         file_path_str = str(file_path)
#         print(file_path.name)
#
#         item = QListWidgetItem(list_widget)
#         item_widget = QLabel(file_path_str)
#         list_widget.setItemWidget(item, item_widget)
#
#         if list_widget.count() > 1:
#             def check_item_widget_y_not_0():
#                 assert item_widget.pos().y() != 0
#             qtbot.waitUntil(check_item_widget_y_not_0)
#
#         top_left_corner_pt1 = tabbed_list_window.videos_tab.listWidget.mapToGlobal(tabbed_list_window.videos_tab.listWidget.pos())
#         # item_widget = list_widget.itemWidget(list_widget.item(list_widget.count() - 1))
#         top_left_corner_pt2 = list_widget.mapToGlobal(item_widget.pos())
#
#         # gui doesn't update with drop item without waiting
#         qtbot.wait(1)
#
#         pyautogui.mouseDown(top_left_corner_pt2.x() + 10, top_left_corner_pt2.y() + 5, duration=1)
#         pyautogui.dragTo(top_left_corner_pt1.x() + 100, top_left_corner_pt1.y() + 50, duration=1)
#         pyautogui.mouseUp()
#
#         # gui doesn't update with drop item without waiting
#         qtbot.wait(1)
#
#         # wait for screenshot to finish loading
#         wait_for_threadpool_to_complete(qtbot, tabbed_list_window.videos_tab.thread_pool)
#
#         save_screenshot(f"drop-screenshot-{file_path.name[:file_path.name.find('.')]}.png")
#
#         # https://www.youtube.com/watch?v=EKVwYkhOTeo
#
#         assert_new_file_item_state(qtbot, tabbed_list_window.videos_tab, file_to_url(file_path_str), cur_num_of_items + 1)
#
#         cur_num_of_items = tabbed_list_window.videos_tab.listWidget.count()
#
#
# @pytest.mark.order(3)
# def test_drop_unsupported_video_into_file_window(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     file_list_state = tabbed_list_window.state.file_list
#     # copy_of_state = copy.deepcopy(file_list_state)
#     # copy_of_state_dict = file_list_state.asdict()
#     # print(copy_of_state_dict)
#
#     list_widget = list_widget_to_test_drag_and_drop()
#     qtbot.addWidget(list_widget)
#     qtbot.waitExposed(list_widget)
#
#     # ffmpeg -i test_vid.mp4 -q:v 0 -q:a 0 test_vid.mpg
#
#     path = video_folder_path().joinpath('unsupported').resolve()
#     for file_path in path.iterdir():
#         file_path_str = str(file_path)
#         print(file_path.name)
#
#         item = QListWidgetItem(list_widget)
#         item_widget = QLabel(file_path_str)
#         list_widget.setItemWidget(item, item_widget)
#
#         if list_widget.count() > 1:
#             def check_item_widget_y_not_0():
#                 assert item_widget.pos().y() != 0
#             qtbot.waitUntil(check_item_widget_y_not_0)
#
#         top_left_corner_pt1 = tabbed_list_window.videos_tab.listWidget.mapToGlobal(tabbed_list_window.videos_tab.listWidget.pos())
#         # item_widget = list_widget.itemWidget(list_widget.item(list_widget.count() - 1))
#         top_left_corner_pt2 = list_widget.mapToGlobal(item_widget.pos())
#
#         # gui doesn't update with drop item without waiting
#         qtbot.wait(1)
#
#         # qtbot.waitUtil doesn't work properly inside the timer
#         timer = QTimer()
#
#         def handle_dialog():
#             print('timer')
#             # since it's a modal window, msg box should be on top
#             if isinstance(QApplication.activeWindow(), QMessageBox):
#                 msg_box = QApplication.activeWindow()
#                 btn = msg_box.defaultButton()
#                 qtbot.mouseClick(btn, Qt.LeftButton)
#                 timer.stop()
#                 timer.deleteLater()
#
#         timer.timeout.connect(handle_dialog)
#         timer.start(500)
#
#         pyautogui.mouseDown(top_left_corner_pt2.x() + 10, top_left_corner_pt2.y() + 5, duration=1)
#         pyautogui.dragTo(top_left_corner_pt1.x() + 100, top_left_corner_pt1.y() + 50, duration=1)
#         pyautogui.mouseUp()
#
#         # gui doesn't update with drop item without waiting
#         qtbot.wait(1)
#
#         save_screenshot(f"drop-screenshot-{file_path.name}.png")
#
#         # compare(copy_of_state, file_list_state)
#
#     # gui doesn't update with drop item without waiting
#     qtbot.wait(1)
#
#     # wait for screenshot to finish loading
#     wait_for_threadpool_to_complete(qtbot, tabbed_list_window.videos_tab.thread_pool)
#
#
# @pytest.mark.order(4)
# def test_open_video_in_file_window(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#
#     list_widget = tabbed_list_window.videos_tab.listWidget
#     for item in list_widget.get_all_items():
#         item_widget = list_widget.itemWidget(item)
#         qtbot.mouseDClick(item_widget, Qt.LeftButton)
#
#         qtbot.wait(5000)
#         break
#
#
# def assert_new_file_item_state(qtbot, file_list_window, new_file_url_added, new_total_count_expected):
#     file_list_state = file_list_window.state.file_list
#
#
#     # assert on state
#     print(f'{len(file_list_state.files)} - {new_total_count_expected}')
#     assert len(file_list_state.files) == new_total_count_expected
#     assert len(file_list_state.files_dict) == new_total_count_expected
#
#     file_item = file_list_state.files[-1]
#     assert file_item.name == new_file_url_added
#     assert len(file_item.tags) == 0
#     assert new_file_url_added.path() in file_list_state.files_dict
#     assert file_list_state.files_dict[new_file_url_added.path()] == file_item
#
#     # assert on widget
#     assert file_list_window.listWidget.count() == new_total_count_expected
#
#     item = file_list_window.listWidget.item(file_list_window.listWidget.count() - 1)
#     item_widget = file_list_window.listWidget.itemWidget(item)
#     item_label = item_widget.findChildren(QLabel, "name")[0].text()
#     assert item_label == new_file_url_added.fileName()
#
#     # wait for screenshot to finish loading
#     wait_for_threadpool_to_complete(qtbot, file_list_window.thread_pool)
#
#     screenshot_label = item_widget.findChildren(QLabel, "screenshot")[0]
#     pixmap = screenshot_label.pixmap()
#     assert pixmap != file_list_window.black_pixmap
#
#
# @pytest.mark.order(100)
# def test_cleanup(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     wait_for_threadpool_to_complete(qtbot, tabbed_list_window.videos_tab.thread_pool)
#     tabbed_list_window.close()
#     preview_window.close()
#     output_window.close()
#     timeline_window.close()
#     print('you succeeded')