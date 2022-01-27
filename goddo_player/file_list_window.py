import logging
import os

import cv2
import imutils
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QUrl, QThreadPool, QRunnable, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QMouseEvent, QKeyEvent, QPixmap
from PyQt5.QtWidgets import (QListWidget, QWidget, QApplication, QVBoxLayout, QLabel, QHBoxLayout, QListWidgetItem,
                             QScrollArea, QStyle)

from goddo_player.app.event_helper import common_event_handling
from goddo_player.utils.draw_utils import numpy_to_pixmap
from goddo_player.widgets.flow import FlowLayout
from goddo_player.utils.message_box_utils import show_error_box
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.signals import StateStoreSignals


class ClipItemWidget(QWidget):
    def __init__(self, url: QUrl, list_widget, default_pixmap: QPixmap):
        super().__init__()
        self.v_margin = 6
        self.list_widget = list_widget
        self.url = url

        lbl = QLabel()
        lbl.setObjectName('screenshot')
        lbl.setFixedHeight(default_pixmap.height())
        lbl.setPixmap(default_pixmap)

        h_layout = QHBoxLayout()
        h_layout.addWidget(lbl)

        widget = QWidget()

        # groupBox = QGroupBox(f'Tags')
        # vbox = QVBoxLayout()

        flow = FlowLayout(margin=1)
        # vbox.addWidget(groupBox)
        widget.setLayout(flow)
        self.flow_layout = flow

        scroll = FileScrollArea(self.list_widget)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        file_name = url.fileName().split(os.sep)[-1]

        v_layout = QVBoxLayout()
        v_layout.addWidget(QLabel(file_name))
        v_layout.addWidget(scroll)
        h_layout.addLayout(v_layout)
        self.setLayout(h_layout)

    def delete_tag(self):
        logging.debug(f'{self.sender()}')
        self.flow_layout.removeWidget(self.sender())


class FileScrollArea(QScrollArea):
    def __init__(self, list_widget: 'QListWidget', parent=None):
        super().__init__(parent)
        self.list_widget = list_widget

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        logging.info('double click')
        super().mouseDoubleClickEvent(a0)

    def eventFilter(self, obj, event: 'QEvent') -> bool:
        if event.type() == QMouseEvent.Enter:
            self.list_widget.blockSignals(True)
            return True
        elif event.type() == QMouseEvent.Leave:
            self.list_widget.blockSignals(False)
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
    def __should_accept_drop(url: 'QUrl'):
        _, ext = os.path.splitext(url.fileName())
        if ext.lower() in PlayerConfigs.supported_video_exts:
            return True
        else:
            return False

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        logging.info(f'drag enter: {event.mimeData().urls()}')
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if not self.__should_accept_drop(url):
                    return
            event.accept()

    # parent class prevents accepting
    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        pass

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        for url in event.mimeData().urls():
            if not url.path().isascii():
                show_error_box(self, "sorry unicode file names are not support!")
                break

            self.signals.add_file_slot.emit(url)


class SceenshotThread(QRunnable):
    def __init__(self, url: QUrl, signal, item: QListWidgetItem):
        super().__init__()
        self.url = url
        self.signal = signal
        self.item = item

    @pyqtSlot()
    def run(self):
        logging.info("started thread to get screenshot")

        cap = cv2.VideoCapture(self.url.path())
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 2))
        _, frame = cap.read()
        frame = imutils.resize(frame, height=108)
        pixmap = numpy_to_pixmap(frame)

        logging.info(f'emitting pixmap back to file list')
        self.signal.emit(pixmap, self.item)


class FileList(QWidget):
    update_screenshot_slot = pyqtSignal(QPixmap, QListWidgetItem)

    def __init__(self):
        super().__init__()
        title_bar_height = QApplication.style().pixelMetric(QStyle.PM_TitleBarHeight)

        self.setGeometry(0, title_bar_height, 500, 1000)
        self.setWindowTitle('中毒美女捜査官')
        self.state_signals: StateStoreSignals = StateStoreSignals()

        vbox = QVBoxLayout(self)
        self.listWidget = FileListWidget()
        self.listWidget.itemDoubleClicked.connect(self.double_clicked)
        vbox.addWidget(self.listWidget)
        self.setLayout(vbox)

        self.black_pixmap = numpy_to_pixmap(np.zeros((108, 192, 1)))
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(10)

        self.update_screenshot_slot.connect(self.update_screenshot_on_item)

    def update_screenshot_on_item(self, pixmap: QPixmap, item: QListWidgetItem):
        item_widget: ClipItemWidget = self.listWidget.itemWidget(item)
        child = item_widget.findChild(QLabel, 'screenshot')
        logging.debug(f'found child {child}')
        child.setPixmap(pixmap)

    def add_video(self, url: 'QUrl'):
        logging.info(f'adding video {url}')

        # Add to list a new item (item is simply an entry in your list)
        item = QListWidgetItem(self.listWidget)

        # Instantiate a custom widget
        row = ClipItemWidget(url, self.listWidget, self.black_pixmap)
        item.setSizeHint(row.minimumSizeHint())

        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, row)

        th = SceenshotThread(url, self.update_screenshot_slot, item)
        self.thread_pool.start(th)

    def double_clicked(self, item):
        item_widget: ClipItemWidget = self.listWidget.itemWidget(item)
        logging.info(f'playing {item_widget.url}')
        self.state_signals.preview_window.switch_video_slot.emit(item_widget.url, True)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        common_event_handling(event, self.signals, self.state)

        super().keyPressEvent(event)
