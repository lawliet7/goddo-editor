
import logging
from PyQt5.QtCore import QRect, Qt, QMimeData, QTime, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QKeyEvent, QPaintEvent, QColor, QMouseEvent, QDrag, \
    QResizeEvent, QWheelEvent, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialog, QTimeEdit
from goddo_player.app.signals import PlayCommand, StateStoreSignals
from goddo_player.app.state_store import StateStore
from goddo_player.utils.enums import PositionType
from goddo_player.utils.time_frame_utils import build_time_str, frames_to_time_components

from goddo_player.utils.time_in_frames_edit import TimeInFramesEdit

class GoToFrameDialog(QObject):
    submit_slot = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__()

        self.state = StateStore()
        self.signals = StateStoreSignals()

        self.time_edit = TimeInFramesEdit()
        self.dialog_start_text = QLabel()
        self.dialog_end_text = QLabel()
        self.dialog_fps_text = QLabel('fps: ')
        self.dialog = QDialog(parent)
        self.dialog.setWindowTitle('Go To Frame')
        self.dialog.setWindowFlag(Qt.WindowContextHelpButtonHint,False)

        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(self.time_edit)
        dialog_layout.addWidget(self.dialog_fps_text)
        dialog_layout.addWidget(self.dialog_start_text)
        dialog_layout.addWidget(self.dialog_end_text)
        self.dialog.setLayout(dialog_layout)
        self.time_edit.editingFinished.connect(self._on_dialog_box_done)
    
    def _on_dialog_box_done(self):
        if self.time_edit.hasFocus():
            logging.debug(f'=== go to value {self.time_edit.value()}')
            self.submit_slot.emit(self.time_edit.value())
            self.close()

    def show_dialog(self, fps, current_frame, min_frame, max_frame):
        self.time_edit.reset(fps, current_frame=current_frame, min_frame=min_frame, max_frame=max_frame)
        start_time_str = build_time_str(*frames_to_time_components(min_frame, fps))
        end_time_str = build_time_str(*frames_to_time_components(max_frame, fps))
        self.dialog_start_text.setText(f'start: {start_time_str}')
        self.dialog_end_text.setText(f'end:  {end_time_str}')
        self.dialog_fps_text.setText(f'fps:   {round(fps,3)}')
        self.dialog.exec_()  # blocks all other windows until this window is closed.

    def close(self):
        self.dialog.close()

    def isHidden(self):
        return self.dialog.isHidden()

    def value(self):
        if not self.isHidden():
            return self.time_edit.value()

    def text(self):
        if not self.isHidden():
            return self.time_edit.text()
        
