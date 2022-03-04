import logging
from queue import Queue, Empty

from PyQt5.QtCore import QTimer, QRect
from PyQt5.QtWidgets import QWidget

from enum import Enum, auto

from goddo_player.app.monarch import MonarchSystem
from goddo_player.utils.window_util import clone_rect
from goddo_test.utils.BlankFullScreenWidget import BlankFullScreenWidget


class Command(Enum):
    SHOW_MAX_WINDOW = auto()
    HIDE_MAX_WINDOW = auto()
    RESET = auto()
    ACTIVATE_FILE_WINDOW = auto()


class CommandWidget(QWidget):
    def __init__(self, monarch: MonarchSystem):
        super().__init__()

        self._q = Queue()
        self._monarch = monarch

        self._list_window_geometry = clone_rect(self._monarch.tabbed_list_window.geometry())
        self._preview_window_geometry = clone_rect(self._monarch.preview_window.geometry())
        self._output_window_geometry = clone_rect(self._monarch.preview_window_output.geometry())
        self._timeline_window_geometry = clone_rect(self._monarch.timeline_window.geometry())

        self._timer = QTimer()
        self._timer.timeout.connect(self._handler)
        self._timer.start(500)

        self._max_widget = BlankFullScreenWidget()
        self._max_widget.hide()

    def _handler(self):
        try:
            cmd = self._q.get_nowait()
            if cmd == Command.RESET:
                self._reset()
            elif cmd == Command.SHOW_MAX_WINDOW:
                self._max_widget.show()
            elif cmd == Command.HIDE_MAX_WINDOW:
                self._max_widget.hide()
            elif cmd == Command.ACTIVATE_FILE_WINDOW:
                self._monarch.tabbed_list_window.activateWindow()
            self._q.task_done()
        except Empty:
            pass
        
    def submit_cmd(self, cmd: Command):
        self._q.put(cmd, True)

    def queue_is_empty(self):
        return self._q.empty()

    def _reset(self):
        self._max_widget.reset()


