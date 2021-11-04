import os
import sys

import cv2
import imutils
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDragEnterEvent, QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import (QListWidget, QWidget, QMessageBox,
                             QApplication, QVBoxLayout, QLabel, QHBoxLayout, QListWidgetItem, QScrollArea, QStyle,
                             QPushButton, QErrorMessage)

from goddo_player.draw_utils import numpy_to_pixmap
from goddo_player.time_frame_utils import frames_to_time_components, build_time_str
from goddo_player.ui.flow import FlowLayout
from goddo_player.ui.message_box_utils import show_error_box
from goddo_player.ui.state_store import State


class MyItemWidget(QWidget):
    def __init__(self, file_path, list_widget):
        super().__init__()
        self.v_margin = 6
        self.list_widget = list_widget
        self.file_path = file_path

        cap = cv2.VideoCapture(file_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 2))
        _, frame = cap.read()
        self.frame = imutils.resize(frame, height=100)
        print(f'frame size={self.frame.shape}')
        pixmap = numpy_to_pixmap(self.frame)

        lbl = QLabel()
        lbl.setFixedHeight(100)
        lbl.setPixmap(pixmap)

        h_layout = QHBoxLayout()
        h_layout.addWidget(lbl)

        widget = QWidget()

        # groupBox = QGroupBox(f'Tags')
        # vbox = QVBoxLayout()

        flow = FlowLayout(margin=1)
        # vbox.addWidget(groupBox)
        # for i in range(50):
        #     btn = QPushButton(f"you suck {i}")
        #     btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        #     btn.clicked.connect(self.delete_tag)
        #     flow.addWidget(btn)
        widget.setLayout(flow)
        self.flow_layout = flow

        scroll = FileScrollArea(self.list_widget)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        # groupBox

        file_name = file_path.split(os.sep)[-1]

        v_layout = QVBoxLayout()
        v_layout.addWidget(QLabel(file_name))
        v_layout.addWidget(scroll)
        h_layout.addLayout(v_layout)
        self.setLayout(h_layout)

    def delete_tag(self):
        print(f'{self.sender()}')
        self.flow_layout.removeWidget(self.sender())


class FileScrollArea(QScrollArea):
    def __init__(self, list_widget: 'QListWidget', parent=None):
        super().__init__(parent)
        self.list_widget = list_widget

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        print('double click')
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
        # self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.accepted_video_formats = ['mp4', 'wmv', 'mkv']

        self.state = State()

    def __should_accept_drop(self, url: 'QUrl'):
        _, ext = os.path.splitext(url.fileName())
        if ext[1:].lower() in self.accepted_video_formats:
            return True
        else:
            return False

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        print('drag enter')
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if not self.__should_accept_drop(url):
                    return
            event.accept()
            print('accepted')
        # event.accept()

    # parent class prevents accepting
    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        pass
    #     self.dragEnterEvent(event)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        for url in event.mimeData().urls():
            print(url.path())
            if not url.path().isascii():
                show_error_box(self, "sorry unicode file names are not support!")
                break
            # State().update_preview_file_slot.emit('source', url)
            self.state.new_file_slot.emit(url.path())

            # time_components = frames_to_time_components(self.video_player.total_frames, self.video_player.fps)
            # self.total_time_str = build_time_str(*time_components)
            # self.__emit_play_event()

            # self.window.setTitle('04.mp4')
            # self.window.requestActivate()

        # file_path = event.mimeData().text()
        # file_name = file_path[file_path.rindex('/') + 1:]
        # no_prefix_file_path = file_path[8:] if file_path.startswith('file:///') else file_path
        # print(f'drop {event.mimeData().urls()}, {file_path}')


class FileList(QWidget):
    def __init__(self):
        super().__init__()
        title_bar_height = QApplication.style().pixelMetric(QStyle.PM_TitleBarHeight)

        self.setGeometry(0, title_bar_height, 500, 1000)
        self.setWindowTitle("強姦方法")

        self.initUI()

        self.state = State()
        self.state.new_file_slot.connect(self.add_video)

    def add_video(self, file_path):
        print(f'adding video {file_path}')
        # Add to list a new item (item is simply an entry in your list)
        item = QListWidgetItem(self.listWidget)

        # Instantiate a custom widget
        row = MyItemWidget(file_path, self.listWidget)
        item.setSizeHint(row.minimumSizeHint())

        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, row)

    def initUI(self):
        vbox = QVBoxLayout(self)

        self.listWidget = FileListWidget()


        list_data = []
        # list_data = [r'C:\Users\William\Downloads\Welcome2Life.CAN.Ep05.mp4',
        #              r'C:\Users\William\Downloads\Ayumi.mp4',
        #              r'C:\Users\William\Downloads\xvsr049.HD.wmv',
        #              # r'C:\Users\William\Downloads\[FOW-002] Kunoichi - Broken Princess (720P).mp4_10526_12568.mp4',
        #              r'C:\Users\William\Downloads\Alice.CAN.Ep05.mp4',
        #              r'C:\Users\William\Downloads\YourHonor.CAN.Ep07.mp4']

        for item in list_data:
            self.addVideo(item)

        self.listWidget.itemDoubleClicked.connect(self.double_clicked)

        vbox.addWidget(self.listWidget)
        self.setLayout(vbox)

    def double_clicked(self, item):
        # QMessageBox.information(self, "Info", item.text())
        item_widget = self.listWidget.itemWidget(item)
        self.state.update_preview_file_slot.emit('source', QUrl(item_widget.file_path))

        print(item_widget)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            self.state.save_slot.emit()
        else:
            super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    ex = FileList()
    ex.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
