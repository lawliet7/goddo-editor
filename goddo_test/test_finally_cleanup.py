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
# @pytest.mark.order(100)
# def test_cleanup(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     wait_for_threadpool_to_complete(qtbot, tabbed_list_window.videos_tab.thread_pool)
#     tabbed_list_window.close()
#     preview_window.close()
#     output_window.close()
#     timeline_window.close()
#     print('you succeeded')
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
