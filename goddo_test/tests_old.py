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