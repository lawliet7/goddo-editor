import logging
from typing import Dict, List

import imutils
import numpy as np

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSlot, pyqtSignal, QMimeData, QEvent
from PyQt5.QtGui import QDrag, QMouseEvent, QPixmap, QKeyEvent, QContextMenuEvent
from PyQt5.QtWidgets import QListWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QListWidgetItem, QScrollArea, QMenu
from goddo_player.app.app_constants import VIDEO_CLIP_DRAG_MIME_TYPE
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils import open_cv_utils
from goddo_player.utils.enums import PositionType

from goddo_player.utils.event_helper import is_key_with_modifiers
from goddo_player.app.signals import PlayCommand, StateStoreSignals
from goddo_player.app.state_store import ClipListStateItem, StateStore, VideoClip
from goddo_player.utils.message_box_utils import show_error_box, show_input_msg_box
from goddo_player.utils.video_path import VideoPath
from goddo_player.utils.draw_utils import numpy_to_pixmap
from goddo_player.widgets.base_qwidget import BaseQWidget
from goddo_player.widgets.flow import FlowLayout
from goddo_player.widgets.tag import TagWidget, TagDialogBox
from goddo_player.list_window.screenshot_thread import ScreenshotThread


class ClipItemWidget(QWidget):
    def __init__(self, clip_name: str, video_clip: VideoClip, list_widget, default_pixmap: QPixmap):
        super().__init__()
        self.v_margin = 6
        self.list_widget = list_widget
        self.video_clip = video_clip

        self.signals: StateStoreSignals = StateStoreSignals()

        self.screenshot_label = QLabel()
        self.screenshot_label.setObjectName('screenshot')
        self.screenshot_label.setFixedHeight(default_pixmap.height())
        self.screenshot_label.setPixmap(default_pixmap)

        v_layout1 = QVBoxLayout()
        
        self.clip_name_label = QLabel(clip_name)
        # self.clip_name_label.setObjectName("name")
        v_layout1.addWidget(self.clip_name_label)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.screenshot_label)

        v_layout1.addLayout(h_layout)

        widget = QWidget()

        # groupBox = QGroupBox(f'Tags')
        # vbox = QVBoxLayout()

        flow = FlowLayout(margin=1)
        # vbox.addWidget(groupBox)
        widget.setLayout(flow)
        self.flow_layout = flow

        scroll = ListClipScrollArea(self)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        self.file_name_label = QLabel(f'{video_clip.video_path.file_name()} : {video_clip.frame_in_out.in_frame} - {video_clip.frame_in_out.out_frame}')
        # self.file_name_label.setObjectName("name")

        v_layout2 = QVBoxLayout()
        v_layout2.addWidget(self.file_name_label)
        v_layout2.addWidget(scroll)
        h_layout.addLayout(v_layout2)
        self.setLayout(v_layout1)

    def __add_tag_callback(self, tag):
        self.signals.remove_clip_tag_slot.emit(self.video_clip, tag)

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

    def get_tags(self):
        tags = []
        for i in range(self.flow_layout.count()):
            tag_widget = self.flow_layout.itemAt(i).widget()
            tags.append(tag_widget.text())
        return tags

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)

        import pickle

        if event.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            data = pickle.dumps(self.video_clip.as_dict())
            mime_data.setData(VIDEO_CLIP_DRAG_MIME_TYPE,data)
            drag.setMimeData(mime_data)
            drag.exec()


class ListClipScrollArea(QScrollArea):
    def __init__(self, item_widget: 'ClipItemWidget', parent=None):
        super().__init__(parent)
        self.item_widget = item_widget

        self.signals = StateStoreSignals()
        self.tag_dialog_box = TagDialogBox()

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        logging.info(f'double click @ {event.pos()}')
        
        if event.buttons() == Qt.LeftButton:

            def remove_tag(tag):
                self.signals.remove_clip_tag_slot.emit(self.item_widget.video_clip, tag)

            def add_tag(tag):
                self.signals.add_clip_tag_slot.emit(self.item_widget.video_clip, tag)

            self.tag_dialog_box.open_modal_dialog(self.item_widget.get_tags(), add_tag, remove_tag)


    def eventFilter(self, obj, event) -> bool:
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


class ClipListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setWindowTitle('美少女捜査官')
        self.setMinimumWidth(500)

        self.signals: StateStoreSignals = StateStoreSignals()
        self.state: StateStore = StateStore()

    def get_all_items(self) -> List[QListWidgetItem]:
        return self.findItems('*', Qt.MatchWildcard)

    def eventFilter(self, obj, event: 'QEvent') -> bool:
        # print(event)
        # print(event.type())
        # print(QEvent.ContextMenu)
        if event.type() == QEvent.ContextMenu: 
            # print(event)
            # print(obj)
            item_widget = obj

            menu = QMenu(self)
            change_clip_name_action = menu.addAction("change clip name")
            action = menu.exec_(event.globalPos())
            if action == change_clip_name_action:
                logging.info('creating clip')

                text, ok = show_input_msg_box(self, 'Enter new clip name', 'new clip name: ', default_text=item_widget.clip_name_label.text())
                if ok:
                    if len(text.strip()) > 2:
                        # clip = self.state.timeline.clips[found_idx]
                        # self.signals.add_clip_slot.emit(text.strip(), clip)
                        print(item_widget.clip_name_label.text())
                        print(text)
                        print('--')
                        self.signals.change_clip_name_slot.emit(text, item_widget.video_clip)
                    else:
                        show_error_box(self, 'Please enter more than 2 characters')

            return True

        return super().eventFilter(obj, event)

class ScreenshotThread(QRunnable):
    def __init__(self, video_clip: VideoClip, signal, item: QListWidgetItem):
        super().__init__()
        self.video_clip = video_clip
        self.signal = signal
        self.item = item

    @pyqtSlot()
    def run(self):
        logging.debug("started thread to get screenshot")

        cap = open_cv_utils.create_video_capture(self.video_clip.video_path.str())

        in_frame = self.video_clip.frame_in_out.get_resolved_in_frame()
        out_frame = self.video_clip.frame_in_out.get_resolved_out_frame(open_cv_utils.get_total_frames(cap))
        frame_no = int((out_frame - in_frame) / 2 + in_frame)
        logging.info(f'getting frame for screenshot in_frame={in_frame},out_frame={out_frame},frame_no={frame_no}')
        
        open_cv_utils.set_cap_pos(cap, frame_no)
        frame = open_cv_utils.get_next_frame(cap)
        frame = imutils.resize(frame, height=108)
        pixmap = numpy_to_pixmap(frame)

        open_cv_utils.free_resources(cap)

        logging.debug(f'emitting pixmap back to clip list')
        self.signal.emit(pixmap, self.item)


class ClipListWindow(BaseQWidget):
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
        self.list_widget = ClipListWidget()
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

    def add_clip(self, video_clip: VideoClip):
        logging.info(f'adding clip {video_clip}')

        # Add to list a new item (item is simply an entry in your list)
        item = QListWidgetItem(self.list_widget)

        # Instantiate a custom widget
        row = ClipItemWidget(video_clip.name, video_clip, self.list_widget, self.black_pixmap)
        item.setSizeHint(row.minimumSizeHint())

        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, row)

        th = ScreenshotThread(video_clip, self.update_screenshot_slot, item)
        self.thread_pool.start(th)

        self.clip_list_dict[video_clip.get_key()] = row

    def double_clicked(self, item):
        self.signals.preview_window.play_cmd_slot.emit(PlayCommand.PAUSE)

        item_widget: ClipItemWidget = self.list_widget.itemWidget(item)
        logging.info(f'playing {item_widget.video_clip.video_path}')

        self.state.timeline.opened_clip_index = -1

        def callback_fn():
            if self.state.preview_window_output.is_max_speed:
                self.signals.preview_window_output.switch_speed_slot.emit()

            self.signals.preview_window_output.seek_slot.emit(item_widget.video_clip.frame_in_out.get_resolved_in_frame(), PositionType.ABSOLUTE)
            self.signals.preview_window_output.play_cmd_slot.emit(PlayCommand.PLAY)

        fn_id = self.signals.fn_repo.push(callback_fn)
        self.signals.preview_window_output.switch_video_slot.emit(item_widget.video_clip.video_path, item_widget.video_clip.frame_in_out, fn_id)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if is_key_with_modifiers(event, Qt.Key_W, ctrl=True):
            logging.info('closing clip')
            self.signals.close_file_slot.emit()

        super().keyPressEvent(event)
