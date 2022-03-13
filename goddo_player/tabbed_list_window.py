from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout

from goddo_player.app.event_helper import common_event_handling
from goddo_player.app.signals import StateStoreSignals
from goddo_player.app.state_store import StateStore
from goddo_player.clip_list_window import ClipListWindow
from goddo_player.file_list_window import FileListWindow
from goddo_player.utils.window_util import get_title_bar_height
from goddo_player.widgets.base_qwidget import BaseQWidget


class TabbedListWindow(BaseQWidget):

    def __init__(self):
        super().__init__()

        self.setGeometry(0, get_title_bar_height(), 500, 1000)
        self.setWindowTitle('中毒美女捜査官')
        self.signals: StateStoreSignals = StateStoreSignals()
        self.state = StateStore()

        self.tabs = QTabWidget()
        self.videos_tab = FileListWindow()
        self.clips_tab = ClipListWindow()
        self.tabs.addTab(self.videos_tab, "Videos")
        self.tabs.addTab(self.clips_tab, "Clips")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
