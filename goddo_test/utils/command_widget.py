import logging
from enum import Enum, auto
from queue import Queue, Empty
from typing import List

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox

from goddo_player.app.monarch import MonarchSystem
from goddo_player.app.signals import PlayCommand
from goddo_player.utils.window_util import clone_rect, activate_window
from goddo_test.utils.blank_full_screen_widget import BlankFullScreenWidget
from goddo_test.utils.list_widget_for_dnd import ListWidgetForDnd
from goddo_test.utils.test_utils import wait_until


class CommandType(Enum):
    SHOW_MAX_WINDOW = auto()
    HIDE_MAX_WINDOW = auto()
    RESET = auto()
    SHOW_DND_WINDOW = auto()
    HIDE_DND_WINDOW = auto()
    ADD_ITEM_DND_WINDOW = auto()
    LOAD_FILE = auto()
    SAVE_FILE = auto()
    CLOSE_FILE = auto()
    MINIMIZE_GODDO_WINDOW = auto()


class Command:
    def __init__(self, cmd_type: CommandType, params: List = []):
        self.cmd_type = cmd_type
        self.params = params

    def __repr__(self):
        return f'Command(cmd_type={self.cmd_type},params={self.params})'


class CommandWidget(QWidget):
    def __init__(self, monarch: MonarchSystem):
        super().__init__()

        self._q: Queue[Command] = Queue()
        self._monarch = monarch

        self._list_window_geometry = clone_rect(self._monarch.tabbed_list_window.geometry())
        self._preview_window_geometry = clone_rect(self._monarch.preview_window.geometry())
        self._output_window_geometry = clone_rect(self._monarch.preview_window_output.geometry())
        self._timeline_window_geometry = clone_rect(self._monarch.timeline_window.geometry())

        self._timer = QTimer()
        self._timer.timeout.connect(self._handler)
        self._timer.start(500)

        self._max_widget = BlankFullScreenWidget()

        self.dnd_widget = ListWidgetForDnd()

    def _handler(self):
        try:
            cmd = self._q.get(timeout=0.1)

            logging.info(f'executing cmd {cmd}')

            if cmd.cmd_type == CommandType.RESET:
                self._reset()
            elif cmd.cmd_type == CommandType.SHOW_MAX_WINDOW:
                self._max_widget.show()
            elif cmd.cmd_type == CommandType.HIDE_MAX_WINDOW:
                self._max_widget.hide()
            elif cmd.cmd_type == CommandType.SHOW_DND_WINDOW:
                self.dnd_widget.show()
            elif cmd.cmd_type == CommandType.HIDE_DND_WINDOW:
                self.dnd_widget.hide()
                self.dnd_widget.list_widget.clear()
            elif cmd.cmd_type == CommandType.ADD_ITEM_DND_WINDOW:
                self.dnd_widget.add_item(cmd.params[0])
            elif cmd.cmd_type == CommandType.LOAD_FILE:
                self._monarch.signals.load_slot.emit(cmd.params[0])
            elif cmd.cmd_type == CommandType.SAVE_FILE:
                self._monarch.signals.save_slot.emit(cmd.params[0])
            elif cmd.cmd_type == CommandType.MINIMIZE_GODDO_WINDOW:
                cmd.params[0].showMinimized()
            self._q.task_done()
        except Empty:
            pass
        
    def submit_cmd(self, cmd: Command):
        self._q.put(cmd, True)

        wait_until(lambda: self.queue_is_empty())

    def queue_is_empty(self):
        return self._q.empty()

    def _reset_all_win_geometry(self):
        self._monarch.tabbed_list_window.setGeometry(self._list_window_geometry)
        self._monarch.preview_window.setGeometry(self._preview_window_geometry)
        self._monarch.preview_window_output.setGeometry(self._output_window_geometry)
        self._monarch.timeline_window.setGeometry(self._timeline_window_geometry)

    def _reset(self):
        logging.info('resetting windows')
        active_window = self._monarch.app.activeWindow()
        if isinstance(active_window, QMessageBox):
            active_window.close()

        self._monarch.preview_window.dialog.close()
        self._monarch.preview_window_output.dialog.close()

        self._max_widget.reset_widget()

        self.dnd_widget.reset_widget()

        self._reset_all_win_geometry()

        self._monarch.tabbed_list_window.showMinimized()
        self._monarch.tabbed_list_window.showNormal()

        self._monarch.preview_window.showMinimized()
        self._monarch.preview_window.showNormal()

        self._monarch.preview_window_output.showMinimized()
        self._monarch.preview_window_output.showNormal()

        self._monarch.timeline_window.showMinimized()
        self._monarch.timeline_window.showNormal()

        self._monarch.signals.close_file_slot.emit()



