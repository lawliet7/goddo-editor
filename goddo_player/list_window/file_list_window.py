import logging
from typing import Dict, List

import cv2
import imutils
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QMouseEvent, QPixmap, QKeyEvent
from PyQt5.QtWidgets import (QListWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QListWidgetItem,
                             QScrollArea, QInputDialog)
from goddo_player.preview_window.frame_in_out import FrameInOut

from goddo_player.utils.event_helper import is_key_with_modifiers
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.signals import PlayCommand, StateStoreSignals
from goddo_player.app.state_store import StateStore
from goddo_player.utils.video_path import VideoPath
from goddo_player.utils.draw_utils import numpy_to_pixmap
from goddo_player.utils.message_box_utils import show_error_box
from goddo_player.widgets.base_qwidget import BaseQWidget
from goddo_player.widgets.flow import FlowLayout
from goddo_player.widgets.tag import TagWidget
from goddo_player.list_window.screenshot_thread import ScreenshotThread


class ClipItemWidget(QWidget):
    def __init__(self, video_path: VideoPath, list_widget, default_pixmap: QPixmap):
        super().__init__()
        self.v_margin = 6
        self.list_widget = list_widget
        self.video_path = video_path

        self.signals: StateStoreSignals = StateStoreSignals()

        self.screenshot_label = QLabel()
        self.screenshot_label.setObjectName('screenshot')
        self.screenshot_label.setFixedHeight(default_pixmap.height())
        self.screenshot_label.setPixmap(default_pixmap)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.screenshot_label)

        widget = QWidget()

        # groupBox = QGroupBox(f'Tags')
        # vbox = QVBoxLayout()

        flow = FlowLayout(margin=1)
        # vbox.addWidget(groupBox)
        widget.setLayout(flow)
        self.flow_layout = flow

        scroll = FileScrollArea(self)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        self.file_name_label = QLabel(video_path.file_name())
        self.file_name_label.setObjectName("name")

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.file_name_label)
        v_layout.addWidget(scroll)
        h_layout.addLayout(v_layout)
        self.setLayout(h_layout)

    def __add_tag_callback(self, tag):
        self.signals.remove_video_tag_slot.emit(self.video_path, tag)

    def add_tag(self, tag: str):
        self.flow_layout.addWidget(TagWidget(tag, delete_cb=self.__add_tag_callback))

    def delete_tag(self, tag: str):
        for i in range(self.flow_layout.count()):
            tag_widget = self.flow_layout.itemAt(i).widget()
            if tag_widget.text() == tag:
                logging.info(f'delete tag {tag_widget} with tag {tag_widget.text()}')
                self.flow_layout.removeWidget(tag_widget)

                if tag_widget:
                    tag_widget.close()
                    tag_widget.deleteLater()
                break


class FileScrollArea(QScrollArea):
    def __init__(self, item_widget: 'ClipItemWidget', parent=None):
        super().__init__(parent)
        self.item_widget = item_widget

        self.signals = StateStoreSignals()

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        logging.info(f'double click @ {event.pos()}')

        text, ok = QInputDialog.getText(self, 'Enter Video Tag Name', 'Tag:')
        if ok:
            self.signals.add_video_tag_slot.emit(self.item_widget.video_path, text)

    def eventFilter(self, obj, event: 'QEvent') -> bool:
        if event.type() == QMouseEvent.Enter:
            self.item_widget.list_widget.blockSignals(True)
            return True
        elif event.type() == QMouseEvent.Leave:
            self.item_widget.list_widget.blockSignals(False)
            return True
        return super().eventFilter(obj, event)

    def event(self, event: QtCore.QEvent) -> bool:
        if event.type() == QMouseEvent.Enter:
            return True
        elif event.type() == QMouseEvent.Leave:
            return True
        return super().event(event)


class FileListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setWindowTitle('美少女捜査官')
        self.setMinimumWidth(500)

        self.signals: StateStoreSignals = StateStoreSignals()

    @staticmethod
    def __should_accept_drop(video_path: VideoPath):
        if video_path.ext().lower() in PlayerConfigs.supported_video_exts:
            return True
        else:
            return False

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        logging.info(f'drag enter: {event.mimeData().urls()}')
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if not self.__should_accept_drop(VideoPath(url)):
                    return
            event.accept()

    # parent class prevents accepting
    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        pass

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        for url in event.mimeData().urls():
            self.signals.add_file_slot.emit(VideoPath(url))

            # on windows (according to stackoverflow), you cannot activate window from different process so if we drop file from windows explorer we cannot activate
            # activateWindow() works fine but if we call QApplication.activeWindow(), it returns None as if activate window is still one from other process
            self.signals.activate_all_windows_slot.emit('tabbed_list_window')

    def get_all_items(self) -> List[QListWidgetItem]:
        return self.findItems('*', Qt.MatchWildcard)


class ScreenshotThread(QRunnable):
    def __init__(self, video_path: VideoPath, signal, item: QListWidgetItem):
        super().__init__()
        self.video_path = video_path
        self.signal = signal
        self.item = item

    @pyqtSlot()
    def run(self):
        logging.debug("started thread to get screenshot")

        cap = cv2.VideoCapture(self.video_path.str())
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 2))
        _, frame = cap.read()
        frame = imutils.resize(frame, height=108)
        pixmap = numpy_to_pixmap(frame)

        logging.debug(f'emitting pixmap back to file list')
        self.signal.emit(pixmap, self.item)


class FileListWindow(BaseQWidget):
    update_screenshot_slot = pyqtSignal(QPixmap, QListWidgetItem)

    def __init__(self):
        super().__init__()
        # title_bar_height = QApplication.style().pixelMetric(QStyle.PM_TitleBarHeight)
        #
        # self.setGeometry(0, title_bar_height, 500, 1000)
        # self.setWindowTitle('中毒美女捜査官')
        self.signals: StateStoreSignals = StateStoreSignals()
        self.state = StateStore()

        vbox = QVBoxLayout(self)
        self.list_widget = FileListWidget()
        self.list_widget.itemDoubleClicked.connect(self.double_clicked)
        vbox.addWidget(self.list_widget)
        self.setLayout(vbox)

        self.black_pixmap = numpy_to_pixmap(np.zeros((108, 192, 1)))
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(10)

        self.update_screenshot_slot.connect(self.update_screenshot_on_item)

        self.clip_list_dict: Dict[str, ClipItemWidget] = {}

    def update_screenshot_on_item(self, pixmap: QPixmap, item: QListWidgetItem):
        item_widget: ClipItemWidget = self.list_widget.itemWidget(item)
        item_widget.screenshot_label.setPixmap(pixmap)

    def add_video(self, video_path: VideoPath):
        logging.info(f'adding video {video_path}')

        # Add to list a new item (item is simply an entry in your list)
        item = QListWidgetItem(self.list_widget)

        # Instantiate a custom widget
        row = ClipItemWidget(video_path, self.list_widget, self.black_pixmap)
        item.setSizeHint(row.minimumSizeHint())

        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, row)

        th = ScreenshotThread(video_path, self.update_screenshot_slot, item)
        self.thread_pool.start(th)

        self.clip_list_dict[video_path.str()] = row

    def double_clicked(self, item):
        item_widget: ClipItemWidget = self.list_widget.itemWidget(item)
        logging.info(f'playing {item_widget.video_path}')
        fn_id = self.signals.fn_repo.push(lambda: self.signals.preview_window.play_cmd_slot.emit(PlayCommand.PLAY))
        logging.info(f'=== playing with fn id {fn_id}')
        logging.info(f'=== emitting {fn_id}')
        self.signals.preview_window.switch_video_slot.emit(item_widget.video_path, FrameInOut(), fn_id)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if is_key_with_modifiers(event, Qt.Key_W, ctrl=True):
            logging.info('closing file')
            self.signals.close_file_slot.emit()

        super().keyPressEvent(event)
