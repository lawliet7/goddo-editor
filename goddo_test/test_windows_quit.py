# import sys
# import time
# from unittest import mock
#
# import pyautogui
# import pytest
# from PyQt5.QtCore import Qt
# from PyQt5.QtWidgets import QWidget
#
# from goddo_player.app.monarch import MonarchSystem
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
# @pytest.fixture(scope='module')
# def tabbed_list_window(monarch):
#     yield monarch.tabbed_list_window
#     monarch.tabbed_list_window.close()
#
# @pytest.fixture(scope='module')
# def preview_window(monarch):
#     yield monarch.preview_window
#     monarch.preview_window.close()
#
# @pytest.fixture(scope='module')
# def output_window(monarch):
#     yield monarch.preview_window_output
#     monarch.preview_window_output.close()
#
# @pytest.fixture(scope='module')
# def timeline_window(monarch):
#     yield monarch.timeline_window
#     monarch.preview_window_output.close()
#
# @pytest.mark.order(3)
# def test_tab_window_quit_with_escape_btn(qtbot, tabbed_list_window):
#     with mock.patch.object(QApplication, "exit"):
#         cur_cnt = QApplication.exit.call_count
#         print(f'cur cnt {cur_cnt}')
#         qtbot.keyPress(tabbed_list_window, Qt.Key_Escape)
#         assert QApplication.exit.call_count == (cur_cnt + 1)
#
# @pytest.mark.order(3)
# def test_videos_tab_quit_with_escape_btn(qtbot, tabbed_list_window):
#     with mock.patch.object(QApplication, "exit"):
#         cur_cnt = QApplication.exit.call_count
#         print(f'cur cnt {cur_cnt}')
#         qtbot.keyPress(tabbed_list_window.videos_tab, Qt.Key_Escape)
#         assert QApplication.exit.call_count == (cur_cnt + 1)
#
# @pytest.mark.order(3)
# def test_clips_tab_quit_with_escape_btn(qtbot, tabbed_list_window):
#     with mock.patch.object(QApplication, "exit"):
#         cur_cnt = QApplication.exit.call_count
#         print(f'cur cnt {cur_cnt}')
#         qtbot.keyPress(tabbed_list_window.clips_tab, Qt.Key_Escape)
#         assert QApplication.exit.call_count == (cur_cnt + 1)
#
#
# # @pytest.mark.order(100)
# # def test_cleanup(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
# #     wait_for_threadpool_to_complete(qtbot, tabbed_list_window.videos_tab.thread_pool)
#     # tabbed_list_window.close()
#     # preview_window.close()
#     # output_window.close()
#     # timeline_window.close()
#
#
# # def test_quit_with_escape_btn(qtbot, monarch, preview_window):
# #     with mock.patch.object(QApplication, "exit"):
# #         qtbot.keyPress(tabbed_list_window.videos_tab, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 1
# #
# #         qtbot.keyPress(preview_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 2
# #
# #         qtbot.keyPress(output_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 3
# #
# #         qtbot.keyPress(timeline_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 4
# #
# #
# # def test_quit_with_escape_btn(qtbot, monarch, preview_window):
# #     with mock.patch.object(QApplication, "exit"):
# #         qtbot.keyPress(tabbed_list_window.videos_tab, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 1
# #
# #         qtbot.keyPress(preview_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 2
# #
# #         qtbot.keyPress(output_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 3
# #
# #         qtbot.keyPress(timeline_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 4
# #
# #
# # def test_quit_with_escape_btn(qtbot, monarch, preview_window):
# #     with mock.patch.object(QApplication, "exit"):
# #         qtbot.keyPress(tabbed_list_window.videos_tab, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 1
# #
# #         qtbot.keyPress(preview_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 2
# #
# #         qtbot.keyPress(output_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 3
# #
# #         qtbot.keyPress(timeline_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 4
# #
# #
# # def test_quit_with_escape_btn(qtbot, monarch, preview_window):
# #     with mock.patch.object(QApplication, "exit"):
# #         qtbot.keyPress(tabbed_list_window.videos_tab, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 1
# #
# #         qtbot.keyPress(preview_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 2
# #
# #         qtbot.keyPress(output_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 3
# #
# #         qtbot.keyPress(timeline_window, Qt.Key_Escape)
# #         assert QApplication.exit.call_count == 4
#
