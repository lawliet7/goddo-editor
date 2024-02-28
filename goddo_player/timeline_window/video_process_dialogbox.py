import datetime
import logging
import pathlib
from typing import Callable

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog, QDialog, QLineEdit, QPushButton

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

        self.setWindowTitle("Process Video")
        self.setModal(True)

        v_layout = QVBoxLayout()

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
        pathlib.Path(base_video_folder).mkdir(parents=True, exist_ok=True)

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
        self._cleanup()
        self.close()

    def closeEvent(self, event):
        logging.info("dialog closing")
        self._cleanup()

    def _process_file(self):
        logging.info(f'processing {self.input_box.text()}')

        self._processing_fn(self.input_box.text())

        self._close()

    def _cleanup(self):
        self._processing_fn = None