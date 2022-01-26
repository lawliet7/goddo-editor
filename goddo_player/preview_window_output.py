import logging
import os

import cv2
from PyQt5.QtCore import QRect, Qt, QUrl, QMimeData
from PyQt5.QtGui import QPainter, QKeyEvent, QPaintEvent, QColor, QMouseEvent, QDrag, \
    QResizeEvent, QWheelEvent
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel

from goddo_player.click_slider import ClickSlider
from goddo_player.utils.enums import IncDec
from goddo_player.app.app_constants import WINDOW_NAME_OUTPUT
from goddo_player.preview_widget import PreviewWidget
from goddo_player.app.signals import StateStoreSignals, PlayCommand, PositionType
from goddo_player.app.state_store import StateStore
from goddo_player.utils.time_frame_utils import build_time_str, frames_to_time_components, frames_to_secs


class PreviewWindowOutput(QWidget):
    def __init__(self):
        super().__init__()
        self.base_title = '美女魔王捜査官'
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

        self.preview_widget = PreviewWidget(self.__on_update_pos, WINDOW_NAME_OUTPUT)
        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_widget)
        vbox.addWidget(self.slider)
        vbox.addWidget(self.label)

        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

        self.time_skip_multiplier = 6

    def update(self):
        super().update()

        self.update_label_text()

    def get_wheel_skip_n_frames(self):
        return self.state.preview_window_output.time_skip_multiplier * 5 * self.state.preview_window_output.fps

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        self.preview_widget.update_frame_pixmap(0)

    def go_to_frame(self, frame_no: int, pos_type: PositionType):
        if self.preview_widget.cap:
            if pos_type is PositionType.ABSOLUTE:
                target_frame_no = frame_no - 1
            else:
                target_frame_no = self.preview_widget.get_cur_frame_no() + frame_no - 1
            target_frame_no = min(max(0, target_frame_no), self.state.preview_window_output.total_frames - 1)

            self.preview_widget.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_no)
            self.preview_widget.update_frame_pixmap(1)
            self.update()

    def __on_update_pos(self, cur_frame_no: int, _):
        frame_no = cur_frame_no - self.state.preview_window_output.cur_start_frame
        pos = self.slider.pct_to_slider_value(frame_no / self.state.preview_window_output.cur_total_frames)
        self.slider.blockSignals(True)
        self.slider.setValue(pos)
        self.slider.blockSignals(False)

        self.update()

    def update_label_text(self):
        if self.preview_widget.cap is not None:
            cur_frame_no = self.preview_widget.get_cur_frame_no()
            start_frame = self.state.preview_window_output.cur_start_frame
            cur_total_frames = self.state.preview_window_output.cur_total_frames

            fps = self.state.preview_window_output.fps
            cur_time_str = build_time_str(*frames_to_time_components(cur_frame_no - start_frame, fps))
            total_time_str = build_time_str(*frames_to_time_components(cur_total_frames, fps))
            speed_txt = 'max' if self.state.preview_window_output.is_max_speed else 'normal'
            skip_txt = self.__build_skip_label_txt()

            self.label.setText(f'{cur_time_str}/{total_time_str}  speed={speed_txt}  skip={skip_txt}'
                               f'  restrict={self.preview_widget.restrict_frame_interval}')
        else:
            self.label.setText("you suck")

    def __build_skip_label_txt(self):
        num_secs = self.state.preview_window_output.time_skip_multiplier * 5 % 60
        num_mins = int(self.state.preview_window_output.time_skip_multiplier * 5 / 60) % 60
        min_txt = f'{num_mins}m ' if num_mins > 0 else ''
        sec_txt = f'{num_secs}s' if num_secs > 0 else ''
        return f'{min_txt}{sec_txt}'

    def on_value_changed(self, value):
        pct = self.slider.slider_value_to_pct(value)
        cur_total_frames = self.state.preview_window_output.cur_total_frames
        start_frame = self.state.preview_window_output.cur_start_frame
        frame_no = int(round(pct * cur_total_frames)) + start_frame
        logging.debug(f'value changed to {value}, frame to {frame_no}, '
                      f'total_frames={self.state.preview_window_output.total_frames}')
        frame_in_out = self.state.preview_window_output.frame_in_out
        if not self.preview_widget.restrict_frame_interval or frame_in_out.contains_frame(frame_no):
            self.signals.preview_window_output.seek_slot.emit(frame_no, PositionType.ABSOLUTE)

    def switch_video(self, url: 'QUrl'):
        self.preview_widget.switch_video(url)

        name, _ = os.path.splitext(url.fileName())
        clip_idx = self.state.timeline.opened_clip_index + 1
        self.setWindowTitle(f'{self.base_title} - clip#{clip_idx} - {name}')

        if url.isEmpty():
            self.slider.blockSignals(True)
            self.slider.setValue(0)
            self.slider.blockSignals(False)
            self.slider.setDisabled(True)
        else:
            self.slider.setDisabled(False)

    def toggle_play_pause(self, cmd: PlayCommand = PlayCommand.TOGGLE):
        self.preview_widget.exec_play_cmd(cmd)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            url = QUrl.fromLocalFile(os.path.abspath(os.path.join('', 'saves', 'a.json')))
            self.signals.save_slot.emit(url)
        elif event.key() == Qt.Key_Space:
            self.signals.preview_window_output.play_cmd_slot.emit(PlayCommand.TOGGLE)
        elif event.key() == Qt.Key_S:
            self.signals.preview_window_output.switch_speed_slot.emit()
        elif event.key() == Qt.Key_I:
            self.signals.preview_window_output.in_frame_slot.emit(self.preview_widget.get_cur_frame_no())
            self.signals.preview_window_output.slider_update_slot.emit()
        elif event.modifiers() == Qt.ShiftModifier and event.key() == Qt.Key_I:
            self.signals.preview_window_output.in_frame_slot.emit(None)
            self.signals.preview_window_output.slider_update_slot.emit()
        elif event.key() == Qt.Key_O:
            self.signals.preview_window_output.out_frame_slot.emit(self.preview_widget.get_cur_frame_no())
            self.signals.preview_window_output.slider_update_slot.emit()
        elif event.modifiers() == Qt.ShiftModifier and event.key() == Qt.Key_O:
            self.signals.preview_window_output.out_frame_slot.emit(None)
            self.signals.preview_window_output.slider_update_slot.emit()
        elif event.key() == Qt.Key_Right:
            self.signals.preview_window_output.play_cmd_slot.emit(PlayCommand.PAUSE)
            self.preview_widget.update_frame_pixmap(1)
            self.update()
        elif event.key() == Qt.Key_BracketLeft:
            frame_in_out = self.state.preview_window_output.frame_in_out
            if frame_in_out.in_frame > 0 or frame_in_out.out_frame > 0:
                self.signals.preview_window_output.play_cmd_slot.emit(PlayCommand.PAUSE)
                frame_diff = frame_in_out.in_frame - self.preview_widget.get_cur_frame_no()
                logging.info(f'bracklet left pressed for frame diff - {frame_diff}')
                self.preview_widget.update_frame_pixmap(frame_diff)
                self.update()
        elif event.key() == Qt.Key_BracketRight:
            frame_in_out = self.state.preview_window_output.frame_in_out
            if frame_in_out.in_frame > 0 or frame_in_out.out_frame > 0:
                self.signals.preview_window_output.play_cmd_slot.emit(PlayCommand.PAUSE)
                frame_diff = frame_in_out.out_frame - self.preview_widget.get_cur_frame_no()
                self.preview_widget.update_frame_pixmap(frame_diff)
                self.update()
        elif event.modifiers() == Qt.KeypadModifier and event.key() == Qt.Key_Plus:
            self.signals.preview_window_output.update_skip_slot.emit(IncDec.INC)
        elif event.modifiers() == Qt.KeypadModifier and event.key() == Qt.Key_Minus:
            self.signals.preview_window_output.update_skip_slot.emit(IncDec.DEC)
        elif event.key() == Qt.Key_F:
            self.preview_widget.restrict_frame_interval = not self.preview_widget.restrict_frame_interval
            self.update()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Left:
            self.signals.preview_window_output.play_cmd_slot.emit(PlayCommand.PAUSE)
            self.preview_widget.update_frame_pixmap(-5)
            self.update()
        else:
            super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)

        frame_in_out = self.state.preview_window_output.frame_in_out
        if frame_in_out.in_frame is not None or frame_in_out.out_frame is not None:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText('source')
            drag.setMimeData(mime_data)
            drag.exec()

    def is_playing(self):
        if self.preview_widget.timer and self.preview_widget.timer.isActive():
            return True
        else:
            return False

    @staticmethod
    def get_num_of_extra_frames(extra_frames_in_secs_config, fps):
        return int(round(extra_frames_in_secs_config * fps))

    def get_extra_frames_on_left(self, pw_state):
        extra_frames_in_secs_config = pw_state.extra_frames_in_secs_config
        extra_frames_config = self.get_num_of_extra_frames(extra_frames_in_secs_config, pw_state.fps)
        in_frame = pw_state.frame_in_out.get_resolved_in_frame()
        in_frame_in_secs = int(round(in_frame / pw_state.fps))

        return extra_frames_config \
            if in_frame_in_secs > extra_frames_in_secs_config \
            else in_frame

    def get_extra_frames_on_right(self, pw_state):
        extra_frames_in_secs_config = pw_state.extra_frames_in_secs_config
        extra_frames_config = self.get_num_of_extra_frames(extra_frames_in_secs_config, pw_state.fps)

        leftover_frames = pw_state.total_frames - pw_state.frame_in_out.get_resolved_out_frame(pw_state.total_frames)
        leftover_frames_in_secs = frames_to_secs(leftover_frames / pw_state.fps)

        return extra_frames_config \
            if leftover_frames_in_secs > extra_frames_in_secs_config \
            else leftover_frames

    def get_total_extra_frames(self, pw_state):
        return self.get_extra_frames_on_left(pw_state) + self.get_extra_frames_on_right(pw_state)

    # def abs_to_relative_frame_no(self, abs_frame_no):
    #     return pw_state.frame_in_out.get_resolved_in_frame() - self.get_extra_frames_on_left()


class FrameInOutSlider(ClickSlider):
    def __init__(self, get_wheel_skip_n_frames, parent=None):
        super().__init__(parent)

        self.state = StateStore()
        self.signals = StateStoreSignals()

        self.signals.preview_window_output.slider_update_slot.connect(lambda: self.update())
        self.get_wheel_skip_time = get_wheel_skip_n_frames

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)

        pen = painter.pen()
        brush = painter.brush()

        # todo: allow the in out frame range to be extended
        frame_in_out = self.state.preview_window_output.frame_in_out
        start_frame = self.state.preview_window_output.cur_start_frame
        cur_total_frames = self.state.preview_window_output.cur_total_frames
        if frame_in_out.in_frame is not None and frame_in_out.out_frame is not None:
            left = int(round((frame_in_out.in_frame - start_frame) / cur_total_frames * self.width()))
            right = int(round((frame_in_out.out_frame - start_frame) / cur_total_frames * self.width()))
            rect = QRect(left, 0, right - left, self.height())
            # logging.debug(f'in out {frame_in_out}, total frames {no_of_frames}, rect={rect}')
            painter.fillRect(rect, QColor(166, 166, 166, alpha=150))
        elif frame_in_out.in_frame is not None:
            # left = int(round(frame_in_out.in_frame / no_of_frames * self.width()))
            left = 0
            rect = QRect(left, 0, self.width(), self.height())
            painter.fillRect(rect, QColor(166, 166, 166, alpha=150))
        elif frame_in_out.out_frame is not None:
            # right = int(round(frame_in_out.out_frame / no_of_frames * self.width()))
            right = self.width()
            rect = QRect(0, 0, right, self.height())
            painter.fillRect(rect, QColor(166, 166, 166, alpha=150))

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.end()

    def wheelEvent(self, event: QWheelEvent) -> None:
        logging.info('wheel event')
        # super().wheelEvent(e)
        if event.angleDelta().y() > 0:
            frame_diff = self.get_wheel_skip_time() * -1
        else:
            frame_diff = self.get_wheel_skip_time()

        self.signals.preview_window_output.seek_slot.emit(frame_diff, PositionType.RELATIVE)
