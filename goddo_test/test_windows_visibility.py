# import sys
# import time
# from unittest import mock
#
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
#     return monarch.tabbed_list_window
#
# @pytest.fixture(scope='module')
# def preview_window(monarch):
#     return monarch.preview_window
#
# @pytest.fixture(scope='module')
# def output_window(monarch):
#     return monarch.preview_window_output
#
# @pytest.fixture(scope='module')
# def timeline_window(monarch):
#     return monarch.timeline_window
#
# @pytest.mark.order(1)
# def test_all_visible(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#
#     qtbot.waitExposed(tabbed_list_window)
#     qtbot.waitExposed(preview_window)
#     qtbot.waitExposed(output_window)
#     qtbot.waitExposed(timeline_window)
#
#     assert tabbed_list_window.isVisible()
#     assert preview_window.isVisible()
#     assert output_window.isVisible()
#     assert timeline_window.isVisible()
#
# @pytest.mark.order(2)
# def test_quit_with_escape_btn(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     with mock.patch.object(QApplication, "exit"):
#         qtbot.keyPress(tabbed_list_window.videos_tab, Qt.Key_Escape)
#         assert QApplication.exit.call_count == 1
#
#         qtbot.keyPress(preview_window, Qt.Key_Escape)
#         assert QApplication.exit.call_count == 2
#
#         qtbot.keyPress(output_window, Qt.Key_Escape)
#         assert QApplication.exit.call_count == 3
#
#         qtbot.keyPress(timeline_window, Qt.Key_Escape)
#         assert QApplication.exit.call_count == 4
#
# def base_test_F2(qtbot, windows_tuple, idx, comparison_threshold=0.9):
#     img_base_windows = grab_all_window_imgs(windows_tuple)
#
#     w = QWidget()
#     w.showMaximized()
#     w.show()
#     qtbot.waitExposed(w)
#
#     windows_tuple[idx].activateWindow()
#
#     # test can fail if activate window isn't fast enough
#     time.sleep(0.2)
#
#     img_new_windows = grab_all_window_imgs(windows_tuple)
#
#     for i in range(len(windows_tuple)):
#         if i == idx:
#             assert cmp_image(img_new_windows[i], img_base_windows[i]) > comparison_threshold
#         else:
#             assert cmp_image(img_new_windows[i], img_base_windows[i]) < comparison_threshold
#
#     qtbot.keyPress(windows_tuple[idx], Qt.Key_F2)
#
#     # qtbot.wait(5000)
#
#     img_new_windows = grab_all_window_imgs(windows_tuple)
#
#     for i in range(len(windows_tuple)):
#         save_screenshot(f'visibility_win_{i}_new.png', img_new_windows[i])
#         save_screenshot(f'visibility_win_{i}_base.png', img_new_windows[i])
#         assert cmp_image(img_new_windows[i], img_base_windows[i]) > comparison_threshold
#         # break
#
#     w.close()
#
# @pytest.mark.order(2)
# def test_file_window_videos_tab_show_all_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     base_test_F2(qtbot, (tabbed_list_window.videos_tab, preview_window, output_window, timeline_window), 0)
#
# # @pytest.mark.order(2)
# # def test_file_window_clips_tab_show_all_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
# #     base_test_F2(qtbot, (tabbed_list_window.clips_tab, preview_window, output_window, timeline_window), 0)
#
# # @pytest.mark.order(2)
# # def test_file_window_clips_tab_show_all_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
# #     base_test_F2(qtbot, (tabbed_list_window, preview_window, output_window, timeline_window), 0)
#
# @pytest.mark.order(2)
# def test_file_window_videos_tab_show_all_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     base_test_F2(qtbot, (tabbed_list_window.videos_tab, preview_window, output_window, timeline_window), 0)
#
# @pytest.mark.order(2)
# def test_preview_window_show_all_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     base_test_F2(qtbot, (tabbed_list_window, preview_window, output_window, timeline_window), 1)
#
# @pytest.mark.order(2)
# def test_output_window_show_all_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     base_test_F2(qtbot, (tabbed_list_window, preview_window, output_window, timeline_window), 2)
#
# @pytest.mark.order(2)
# def test_timeline_window_show_all_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     base_test_F2(qtbot, (tabbed_list_window, preview_window, output_window, timeline_window), 3)
#
# def base_test_minimized_F2(qtbot, windows_tuple, idx, comparison_threshold=0.9):
#     img_base_windows = grab_all_window_imgs(windows_tuple)
#
#     for i in range(len(windows_tuple)):
#         if idx != i:
#             windows_tuple[idx].showMinimized()
#
#     # test can fail if restoring window isn't fast enough
#     time.sleep(0.2)
#
#     img_new_windows = grab_all_window_imgs(windows_tuple)
#
#     for i in range(len(windows_tuple)):
#         if i == idx:
#             assert cmp_image(img_new_windows[i], img_base_windows[i]) > comparison_threshold
#         else:
#             assert cmp_image(img_new_windows[i], img_base_windows[i]) < comparison_threshold
#
#     qtbot.keyPress(windows_tuple[idx], Qt.Key_F2)
#
#     img_new_windows = grab_all_window_imgs(windows_tuple)
#
#     for i in range(len(windows_tuple)):
#         assert cmp_image(img_new_windows[i], img_base_windows[i]) > comparison_threshold
#
# # @pytest.mark.order(2)
# # def test_file_window_minimize_and_restore_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
# #     base_test_F2(qtbot, (tabbed_list_window, preview_window, output_window, timeline_window), 0)
#
# @pytest.mark.order(2)
# def test_preview_window_minimize_and_restore_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     base_test_F2(qtbot, (tabbed_list_window, preview_window, output_window, timeline_window), 1)
#
# @pytest.mark.order(2)
# def test_output_window_minimize_and_restore_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     base_test_F2(qtbot, (tabbed_list_window, preview_window, output_window, timeline_window), 2)
#
# @pytest.mark.order(2)
# def test_timeline_window_minimize_and_restore_win_with_F2(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     base_test_F2(qtbot, (tabbed_list_window, preview_window, output_window, timeline_window), 3)
#
# @pytest.mark.order(2)
# def test_a(qtbot, tabbed_list_window, preview_window, output_window, timeline_window):
#     wait_for_threadpool_to_complete(qtbot, tabbed_list_window.videos_tab.thread_pool)
#     tabbed_list_window.close()
#     preview_window.close()
#     output_window.close()
#     timeline_window.close()
#     print('you succeeded')
