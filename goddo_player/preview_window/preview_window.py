import logging
import os

import cv2
from PyQt5.QtCore import QRect, Qt, QMimeData, QTime
from PyQt5.QtGui import QPainter, QKeyEvent, QPaintEvent, QColor, QMouseEvent, QDrag, \
    QResizeEvent, QWheelEvent, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialog, QTimeEdit

from goddo_player.app.app_constants import WINDOW_NAME_SOURCE
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.event_helper import common_event_handling, is_key_with_modifiers
from goddo_player.app.signals import StateStoreSignals, PlayCommand, PositionType
from goddo_player.app.state_store import StateStore
from goddo_player.utils.go_to_frame_dialog import GoToFrameDialog
from goddo_player.utils.time_in_frames_edit import TimeInFramesEdit
from goddo_player.utils.video_path import VideoPath
from goddo_player.preview_window.click_slider import ClickSlider
from goddo_player.preview_window.preview_widget import PreviewWidgetNew
from goddo_player.utils.enums import IncDec
from goddo_player.utils.time_frame_utils import build_time_str, frames_to_time_components


class PreviewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.base_title = '美女天使捜査官'
        self.setWindowTitle(self.base_title)

        self.state = StateStore()
        self.signals = StateStoreSignals()

        self.cap = None

        # self.setMinimumSize(640, 360)
        # self.resize(self.minimumSize())
        self.setAcceptDrops(True)

        self.slider = FrameInOutSlider(self.get_wheel_skip_n_frames, Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setRange(0, 200)
        self.slider.valueChanged.connect(self.on_value_changed)
        self.slider.setFixedHeight(20)
        self.slider.setDisabled(True)

        # p = self.palette()
        # p.setColor(self.backgroundRole(), Qt.black)
        # self.setPalette(p)
        # self.setAutoFillBackground(True)

        self.label = QLabel()
        self.label.setText("you suck")
        self.label.setFixedHeight(15)

        self.preview_widget = PreviewWidgetNew(self.update, self.get_preview_window_state(), self.get_preview_window_signal())
        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_widget)
        vbox.addWidget(self.slider)
        vbox.addWidget(self.label)

        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

        self.dialog = GoToFrameDialog(self)
        self.dialog.submit_slot.connect(self.dialog_box_done)

    def get_preview_window_state(self):
        return self.state.preview_window
    
    def get_preview_window_signal(self):
        return self.signals.preview_window
    
    def dialog_box_done(self, value):
        self.get_preview_window_signal().seek_slot.emit(value, PositionType.ABSOLUTE)

    def update(self):
        super().update()

        self.update_label_text()
        self.update_slider()

    def get_wheel_skip_n_frames(self):
        return self.get_preview_window_state().time_skip_multiplier * 5 * self.get_preview_window_state().fps

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        self.preview_widget.go_to_frame(0, PositionType.RELATIVE)
        self.update()

    def go_to_frame(self, frame_no: int, pos_type: PositionType):
        self.preview_widget.go_to_frame(frame_no, pos_type)
        self.update()

    def update_label_text(self):
        if self.preview_widget.cap is not None:
            cur_total_frames = self.get_preview_window_state().cur_total_frames
            cur_frame_no = self.preview_widget.get_cur_frame_no()

            fps = self.get_preview_window_state().fps
            cur_time_str = build_time_str(*frames_to_time_components(cur_frame_no, fps))
            total_time_str = build_time_str(*frames_to_time_components(cur_total_frames, fps))
            speed_txt = 'max' if self.get_preview_window_state().is_max_speed else 'normal'
            skip_txt = self.__build_skip_label_txt()

            self.label.setText(f'{cur_time_str}/{total_time_str}  speed={speed_txt}  skip={skip_txt}')
        else:
            self.label.setText('you suck')

    def update_slider(self):
        if self.preview_widget.cap is not None:
            if not self.slider.isEnabled:
                self.slider.setEnabled(True)
            
            total_frames = self.get_preview_window_state().total_frames
            cur_frame_no = self.preview_widget.get_cur_frame_no()

            slider_value = int(round(cur_frame_no / total_frames * self.slider.maximum()))

            if self.slider.value() != slider_value:
                self.slider.blockSignals(True)
                self.slider.setValue(slider_value)
                self.slider.blockSignals(False)

    def __build_skip_label_txt(self):
        num_secs = self.get_preview_window_state().time_skip_multiplier * 5 % 60
        num_mins = int(self.get_preview_window_state().time_skip_multiplier * 5 / 60) % 60
        min_txt = f'{num_mins}m' if num_mins > 0 else ''
        sec_txt = f'{num_secs}s' if num_secs > 0 else ''
        return f'{min_txt}{sec_txt}'

    def on_value_changed(self, value):
        frame_no = int(round(self.slider.slider_value_to_pct(value) * self.get_preview_window_state().total_frames))
        logging.debug(f'value changed to {value}, frame to {frame_no}, '
                      f'total_frames={self.get_preview_window_state().total_frames}')
        self.get_preview_window_signal().seek_slot.emit(frame_no, PositionType.ABSOLUTE)

    def _update_state_for_new_video(self, video_path: VideoPath, frame_in_out: FrameInOut):
        preview_window_state = self.get_preview_window_state()
        preview_window_state.video_path = video_path
        preview_window_state.frame_in_out = frame_in_out
        preview_window_state.restrict_frame_interval = False
        preview_window_state.fps = self.preview_widget.get_fps()
        preview_window_state.total_frames = self.preview_widget.get_total_frames()
        preview_window_state.current_frame_no = frame_in_out.get_resolved_in_frame()
        preview_window_state.cur_total_frames = preview_window_state.total_frames
        preview_window_state.cur_start_frame = 1
        preview_window_state.cur_end_frame = preview_window_state.total_frames

    def _update_state_for_blank_video(self, video_path: VideoPath):
        preview_window_state = self.get_preview_window_state()
        preview_window_state.video_path = video_path
        preview_window_state.frame_in_out = FrameInOut()
        preview_window_state.restrict_frame_interval = False
        preview_window_state.fps = 0
        preview_window_state.total_frames = 0
        preview_window_state.current_frame_no = 0
        preview_window_state.cur_total_frames = 0
        preview_window_state.cur_start_frame = 0
        preview_window_state.cur_end_frame = 0

    def switch_video(self, video_path: VideoPath, frame_in_out: FrameInOut):
        self.preview_widget.switch_video(video_path)

        if video_path.is_empty():
            self._update_state_for_blank_video(video_path)
            self.slider.blockSignals(True)
            self.slider.setValue(0)
            self.slider.blockSignals(False)
            self.slider.setDisabled(True)
            self.setWindowTitle(f'{self.base_title}')
        else:
            self._update_state_for_new_video(video_path, frame_in_out)
            self.setWindowTitle(self.base_title + ' - ' + video_path.file_name(include_ext=False))
            self.slider.setDisabled(False)

        self.update()

    def toggle_play_pause(self, cmd: PlayCommand = PlayCommand.TOGGLE):
        if self.preview_widget.cap:
            self.preview_widget.exec_play_cmd(cmd)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        common_event_handling(event, self.signals, self.state)

        if event.key() == Qt.Key_Space:
            self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.TOGGLE)
        elif event.key() == Qt.Key_S:
            self.get_preview_window_signal().switch_speed_slot.emit()
        elif is_key_with_modifiers(event, Qt.Key_I, shift=True):
            self.get_preview_window_signal().in_frame_slot.emit(-1)
            self.get_preview_window_signal().slider_update_slot.emit()
        elif event.key() == Qt.Key_I:
            self.get_preview_window_signal().in_frame_slot.emit(self.preview_widget.get_cur_frame_no())
            self.get_preview_window_signal().slider_update_slot.emit()
        elif is_key_with_modifiers(event, Qt.Key_O, shift=True):
            self.get_preview_window_signal().out_frame_slot.emit(-1)
            self.get_preview_window_signal().slider_update_slot.emit()
        elif event.key() == Qt.Key_O:
            self.get_preview_window_signal().out_frame_slot.emit(self.preview_widget.get_cur_frame_no())
            self.get_preview_window_signal().slider_update_slot.emit()
        elif event.key() == Qt.Key_Right:
            self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.PAUSE)
            self.get_preview_window_signal().seek_slot.emit(1, PositionType.RELATIVE)
        elif event.key() == Qt.Key_BracketLeft:
            frame_in_out = self.get_preview_window_state().frame_in_out
            if frame_in_out.in_frame:
                self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.PAUSE)
                frame_diff = frame_in_out.in_frame - self.preview_widget.get_cur_frame_no()
                self.get_preview_window_signal().seek_slot.emit(frame_diff, PositionType.RELATIVE)
        elif event.key() == Qt.Key_BracketRight:
            frame_in_out = self.get_preview_window_state().frame_in_out
            if frame_in_out.out_frame:
                self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.PAUSE)
                frame_diff = frame_in_out.out_frame - self.preview_widget.get_cur_frame_no()
                self.get_preview_window_signal().seek_slot.emit(frame_diff, PositionType.RELATIVE)
        elif is_key_with_modifiers(event, Qt.Key_Plus, numpad=True):
            self.get_preview_window_signal().update_skip_slot.emit(IncDec.INC)
        elif is_key_with_modifiers(event, Qt.Key_Minus, numpad=True):
            self.get_preview_window_signal().update_skip_slot.emit(IncDec.DEC)
        elif event.key() == Qt.Key_G:
            if self.preview_widget.cap is not None:
                pw_state = self.get_preview_window_state()
                self.dialog.show_dialog(pw_state.fps, current_frame=pw_state.current_frame_no, max_frame=pw_state.total_frames, min_frame=1)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Left:
            self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.PAUSE)
            self.get_preview_window_signal().seek_slot.emit(-5, PositionType.RELATIVE)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)

        frame_in_out = self.get_preview_window_state().frame_in_out
        if frame_in_out.in_frame is not None or frame_in_out.out_frame is not None:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText('source')
            drag.setMimeData(mime_data)
            drag.exec()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        urls = event.mimeData().urls()

        if len(urls) == 1:
            filename = urls[0].fileName()
            _, ext = os.path.splitext(filename)
            if ext in PlayerConfigs.supported_video_exts:
                event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        logging.info(f'drop {event.mimeData().urls()}')

        video_path = VideoPath(event.mimeData().urls()[0])

        self.get_preview_window_signal().switch_video_slot.emit(video_path, FrameInOut())
        self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.PLAY)
        self.signals.add_file_slot.emit(video_path)

    def is_playing(self):
        if self.preview_widget.timer and self.preview_widget.timer.isActive():
            return True
        else:
            return False

class TimeSelectWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.show()

class FrameInOutSlider(ClickSlider):
    def __init__(self, get_wheel_skip_n_frames, parent=None):
        super().__init__(parent)

        self.state = StateStore()
        self.signals = StateStoreSignals()

        self.signals.preview_window.slider_update_slot.connect(lambda: self.update())
        self.get_wheel_skip_time = get_wheel_skip_n_frames

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)

        pen = painter.pen()
        brush = painter.brush()

        frame_in_out = self.state.preview_window.frame_in_out
        total_frames = self.state.preview_window.total_frames
        if frame_in_out.in_frame is not None and frame_in_out.out_frame is not None:
            left = int(round(frame_in_out.in_frame / total_frames * self.width()))
            right = int(round(frame_in_out.out_frame / total_frames * self.width()))
            rect = QRect(left, 0, right - left, self.height())
            logging.debug(f'in out {frame_in_out}, total frames {total_frames}, rect={rect}')
            painter.fillRect(rect, QColor(166, 166, 166, alpha=150))
        elif frame_in_out.in_frame is not None:
            left = int(round(frame_in_out.in_frame / total_frames * self.width()))
            rect = QRect(left, 0, self.width(), self.height())
            painter.fillRect(rect, QColor(166, 166, 166, alpha=150))
        elif frame_in_out.out_frame is not None:
            right = int(round(frame_in_out.out_frame / total_frames * self.width()))
            rect = QRect(0, 0, right, self.height())
            painter.fillRect(rect, QColor(166, 166, 166, alpha=150))

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.end()

    def wheelEvent(self, event: QWheelEvent) -> None:
        logging.debug('wheel event')

        if event.angleDelta().y() > 0:
            frame_diff = self.get_wheel_skip_time() * -1
        else:
            frame_diff = self.get_wheel_skip_time()
        frame_diff = int(frame_diff)

        self.signals.preview_window.seek_slot.emit(frame_diff, PositionType.RELATIVE)
