import sys
import time
from unittest import mock

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from goddo_player.app.monarch import MonarchSystem


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


@pytest.mark.order(1)
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


@pytest.mark.order(2)
def test_file_window_show_all_win_with_F2(qtbot, file_window, preview_window, output_window, timeline_window):
    assert not file_window.isMinimized()
    assert not preview_window.isMinimized()
    assert not output_window.isMinimized()
    assert not timeline_window.isMinimized()

    time.sleep(3)

    # file_window.showMinimized()
    preview_window.showMinimized()
    output_window.showMinimized()
    timeline_window.showMinimized()

    time.sleep(3)

    assert not file_window.isMinimized()
    assert preview_window.isMinimized()
    assert output_window.isMinimized()
    assert timeline_window.isMinimized()

    qtbot.keyPress(file_window, Qt.Key_F2)

    time.sleep(3)

    assert not file_window.isMinimized()
    assert not preview_window.isMinimized()
    assert not output_window.isMinimized()
    assert not timeline_window.isMinimized()


