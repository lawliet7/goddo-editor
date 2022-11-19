from dataclasses import dataclass

import logging
from typing import List

from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtCore import QRect, Qt, QEvent, QPoint
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QPen, QMouseEvent
from PyQt5.QtWidgets import QLabel, QFrame, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea, QDialog, QLineEdit, QPushButton

from goddo_player.app.signals import StateStoreSignals
from goddo_player.utils.draw_utils import draw_lines
from goddo_player.utils.event_helper import is_key_press
from goddo_player.utils.message_box_utils import show_error_box
from goddo_player.utils.video_path import VideoPath
from goddo_player.widgets.flow import FlowLayout

class TagWidget(QLabel):
    def __init__(self, text, delete_cb=None, tag_widget_height=25):
        super().__init__()

        self.setFixedHeight(tag_widget_height)
        self.baseTagColor = QColor(229, 246, 249)
        self.pen_for_x = QPen(QColor(8, 94, 185), 3, Qt.SolidLine, Qt.RoundCap)

        self.setText(text)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        rgb_str = f'rgb({self.baseTagColor.red()}, {self.baseTagColor.green()}, {self.baseTagColor.blue()})'
        self.setStyleSheet(f'background-color: {rgb_str};')
        self.setLineWidth(10)

        self.is_mouse_over = False

        self.rect_coor = _RectCoordinate(self.width(), self.height(), 10, 3)

        self.delete_cb = delete_cb

    def initPainter(self, painter: QPainter) -> None:
        super().initPainter(painter)

        # it gets resized after displaying text only, the one in init is completely wrong
        self.rect_coor = _RectCoordinate(self.width(), self.height(), 10, 3)

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        if self.is_mouse_over:
            painter = QPainter(self)

            painter.fillRect(self.rect_coor.to_rect(), self.baseTagColor)
            draw_lines(painter, self.rect_coor.get_lines(), pen=self.pen_for_x)

            painter.end()

    def enterEvent(self, event: QEvent) -> None:
        super().enterEvent(event)

        self.is_mouse_over = True
        self.update()

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)

        self.is_mouse_over = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)

        if self.rect_coor.is_in_rect(event.pos()):
            self.delete_cb(self.text())


@dataclass
class _RectCoordinate:
    tag_widget_width: int
    tag_widget_height: int
    length: int
    right_margin: int

    def __post_init__(self):
        self.left = self.tag_widget_width - self.right_margin - self.length
        self.right = self.tag_widget_width - self.right_margin
        self.top = self.tag_widget_height / 2 - self.length / 2
        self.bottom = self.tag_widget_height / 2 + self.length / 2

    def to_rect(self):
        return QRect(self.left, self.top, self.length, self.length)

    def get_lines(self):
        return [
            (self.left, self.top, self.right, self.bottom),
            (self.left, self.bottom, self.right, self.top)
        ]

    def is_in_rect(self, pt: QPoint):
        return self.left <= pt.x() <= self.right and self.top <= pt.y() <= self.bottom

class TagDialogBox(QDialog):
    def __init__(self):
        super().__init__()

        self.video_path = None
        self.orig_tags = []
        self.tags = []
        self.signals = StateStoreSignals()

        self.setWindowTitle("Enter Tags")
        self.setModal(True)

        v_layout = QVBoxLayout()
        
        widget = QWidget()
        flow = FlowLayout(margin=1)
        widget.setLayout(flow)
        self.flow_layout = flow

        scroll = QScrollArea(self)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        v_layout.addWidget(scroll)

        h_layout = QHBoxLayout()
        self.input_box = QLineEdit(self)

        add_btn = QPushButton('Add')
        add_btn.clicked.connect(self._add_tag_in_textbox)

        h_layout.addWidget(self.input_box)
        h_layout.addWidget(add_btn)

        v_layout.addLayout(h_layout)

        ok_btn = QPushButton('ok')
        ok_btn.clicked.connect(self._submit_tags)
        cancel_btn = QPushButton('cancel')
        cancel_btn.clicked.connect(self.close)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(ok_btn)
        h_layout2.addWidget(cancel_btn)
        v_layout.addLayout(h_layout2)

        self.setLayout(v_layout)

    def open_modal_dialog(self, video_path: VideoPath, tags: List[str]):
        logging.info('opening dialog')
        logging.info(f'flow layout count {self.flow_layout.count()}')

        self.video_path = video_path
        self.orig_tags = tags[:]
        for tag in tags:
            self._add_tag(tag)
        logging.info(f'flow layout count after adding tags {self.flow_layout.count()}')
        self.open()
        self.input_box.setFocus()

    def _add_tag_in_textbox(self):
        self._add_tag(self.input_box.text())

    def _add_tag(self, tag: str):
        logging.debug(f'adding tag: {tag}')

        if tag.lower() in [x.lower() for x in self.tags]:
            show_error_box(self, 'tag already exists!')
        else:
            self.flow_layout.addWidget(TagWidget(tag, delete_cb=self._delete_tag))
            self.tags.append(tag)

            self.input_box.clear()

    def _delete_tag(self, tag: str):
        logging.info(f'before deleting tag count {self.flow_layout.count()} for tag {tag}')
        for i in range(self.flow_layout.count()):
            tag_widget = self.flow_layout.itemAt(i).widget()
            logging.info(f'searching for tag {tag} with widget tag {tag_widget.text()}')
            if tag_widget.text() == tag:
                logging.info(f'delete tag {tag_widget} with tag {tag_widget.text()}')
                self.flow_layout.removeWidget(tag_widget)

                if tag_widget:
                    tag_widget.close()
                    tag_widget.deleteLater()

                self.tags.remove(tag)
                break
        logging.info(f'after deleting tag count {self.flow_layout.count()}')

    def _submit_tags(self):
        for tag in self.orig_tags:
            logging.info(f'removing tag {tag}')
            self.signals.remove_video_tag_slot.emit(self.video_path, tag)

        for tag in self.tags:
            logging.info(f'adding tag {tag}')
            self.signals.add_video_tag_slot.emit(self.video_path, tag)
        
        self.close()

    def closeEvent(self, event):
        logging.info("dialog closing")
        self._cleanup()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if is_key_press(event, Qt.Key_Escape):
            logging.info("dialog closing")
            self._cleanup()

        super().keyPressEvent(event)

    def _cleanup(self):
        logging.info(f'cleaning up tags {self.tags}')
        while self.tags:
            tag = self.tags[0]
            logging.info(f'cleaning up, deleting tag {tag}')
            self._delete_tag(tag)

        self.tags = []
        self.orig_tags = []
        self.input_box.clear()
        self.video_path = None
