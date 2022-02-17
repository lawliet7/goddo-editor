from PyQt5.QtWidgets import QLabel

from goddo_test.test_utils import wait_for_threadpool_to_complete


def assert_new_file_item_state(qtbot, file_window, new_file_url_added, new_total_count_expected):
    file_list_state = file_window.state.file_list

    # assert on state
    file_item = file_list_state.files[-1]
    assert len(file_list_state.files) == new_total_count_expected
    assert len(file_list_state.files_dict) == new_total_count_expected
    assert file_item.name == new_file_url_added
    assert len(file_item.tags) == 0
    assert new_file_url_added.path() in file_list_state.files_dict
    assert file_list_state.files_dict[new_file_url_added.path()] == file_item

    # assert on widget
    assert file_window.listWidget.count() == new_total_count_expected

    item = file_window.listWidget.item(file_window.listWidget.count() - 1)
    item_widget = file_window.listWidget.itemWidget(item)
    item_label = item_widget.findChildren(QLabel, "name")[0].text()
    assert item_label == new_file_url_added.fileName()

    # wait for screenshot to finish loading
    wait_for_threadpool_to_complete(qtbot, file_window.thread_pool)

    screenshot_label = item_widget.findChildren(QLabel, "screenshot")[0]
    pixmap = screenshot_label.pixmap()
    assert pixmap != file_window.black_pixmap
