import datetime
import logging
import pathlib
import time
from typing import Callable, List

from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtCore import QRect, Qt, QEvent, QPoint
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QPen, QMouseEvent
from PyQt5.QtWidgets import QLabel, QFrame, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFileDialog, QDialog, QLineEdit, QPushButton

from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.state_store import StateStore

class VideoProcessDialogBox(QDialog):
    def __init__(self):
        super().__init__()

        self.orig_tags = []
        self.tags = []
        self.add_tag_fn = None
        self.remove_tag_fn = None

        self.state = StateStore()

        self.setWindowTitle("Enter Tags")
        self.setModal(True)

        v_layout = QVBoxLayout()
        
        # widget = QWidget()
        # flow = FlowLayout(margin=1)
        # widget.setLayout(flow)
        # self.flow_layout = flow

        # scroll = QScrollArea(self)
        # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # scroll.setWidgetResizable(True)
        # scroll.setWidget(widget)

        # v_layout.addWidget(scroll)

        h_layout = QHBoxLayout()
        self.input_box = QLineEdit(self)

        add_btn = QPushButton('Browse')
        add_btn.clicked.connect(self._choose_output_file)

        h_layout.addWidget(self.input_box)
        h_layout.addWidget(add_btn)

        v_layout.addLayout(h_layout)

        ok_btn = QPushButton('ok')
        ok_btn.clicked.connect(self._process_file)
        cancel_btn = QPushButton('cancel')
        cancel_btn.clicked.connect(self.close)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(ok_btn)
        h_layout2.addWidget(cancel_btn)
        v_layout.addLayout(h_layout2)

        self.setLayout(v_layout)

        self._processing_fn = None

    def _get_default_output_file_path(self):
        base_video_folder = PlayerConfigs.base_output_folder.joinpath('Videos')
        save_file_name_no_ext = pathlib.Path(str(self.state.cur_save_file)).stem
        output_file_name = f'output_{save_file_name_no_ext}_{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.mp4'

        return base_video_folder.joinpath(output_file_name)

    def open_modal_dialog(self, processing_fn: Callable[[str], None]):
        logging.info('opening dialog')

        self.input_box.setText(str(self._get_default_output_file_path()))
        self._processing_fn = processing_fn

        self.exec_()

    def _choose_output_file(self):
        file, ext = QFileDialog.getSaveFileName(self, 'Save output video file', self.input_box.text(), "*.mp4;;*.mkv","*.mp4")

        if file:
            logging.info(f'====== {file}')
            self.input_box.setText(file)

    def _close(self):
        # for tag in self.orig_tags:
        #     logging.info(f'removing tag {tag}')
        #     self.remove_tag_fn(tag)

        # for tag in self.tags:
        #     logging.info(f'adding tag {tag}')
        #     self.add_tag_fn(tag)
        
        self._processing_fn = None

        self.close()

    def closeEvent(self, event):
        logging.info("dialog closing")
        # self._cleanup()

    def _process_file(self):
        logging.info(f'====== processing {self.input_box.text()}')

        self._processing_fn(self.input_box.text())

        self._close()

    # def keyPressEvent(self, event: QKeyEvent) -> None:
    #     if is_key_press(event, Qt.Key_Escape):
    #         logging.info("dialog closing")
    #         self._cleanup()

    #     super().keyPressEvent(event)

    # def _cleanup(self):
    #     logging.info(f'cleaning up tags {self.tags}')
    #     while self.tags:
    #         tag = self.tags[0]
    #         logging.info(f'cleaning up, deleting tag {tag}')
    #         self._delete_tag(tag)

    #     self.tags = []
    #     self.orig_tags = []
    #     self.input_box.clear()
    #     self.video_path = None