import logging

import cv2
from PyQt5.QtCore import QRect, Qt, QMimeData
from PyQt5.QtGui import QPainter, QKeyEvent, QPaintEvent, QColor, QMouseEvent, QDrag, \
    QResizeEvent, QWheelEvent, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialog, QHBoxLayout, QInputDialog

from goddo_player.app.app_constants import WINDOW_NAME_OUTPUT
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.draw_utils import text_with_color
from goddo_player.utils.event_helper import common_event_handling, is_key_press, is_key_with_modifiers
from goddo_player.app.signals import StateStoreSignals, PlayCommand, PositionType
from goddo_player.app.state_store import StateStore
from goddo_player.utils.go_to_frame_dialog import GoToFrameDialog
from goddo_player.utils.time_in_frames_edit import TimeInFramesEdit
from goddo_player.utils.video_path import VideoPath
from goddo_player.preview_window.click_slider import ClickSlider
from goddo_player.preview_window.preview_widget import PreviewWidgetNew
from goddo_player.utils.enums import IncDec
from goddo_player.utils.time_frame_utils import build_time_str, frames_to_time_components, frames_to_secs


class PreviewWindowOutput(QWidget):
    def __init__(self):
        super().__init__()
        self.base_title = '血手美女捜査官'
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

        self.time_label = QLabel()
        self.time_label.setText(f"{build_time_str()}/{build_time_str()}")
        self.time_label.setFixedHeight(15)
        self.time_label.setStyleSheet("border:1px solid rgb(0, 0, 255); ")

        self.speed_label = QLabel()
        self.speed_label.setText("speed=normal")
        self.speed_label.setFixedHeight(15)
        self.speed_label.setStyleSheet("border:1px solid rgb(0, 255, 0); ")

        self.skip_label = QLabel()
        self.skip_label.setText("skip=5s")
        self.skip_label.setFixedHeight(15)
        self.skip_label.setStyleSheet("border:1px solid rgb(0, 0, 255); ")

        self.restrict_label = QLabel()
        self.restrict_label.setText("restrict=True")
        self.restrict_label.setFixedHeight(15)
        self.restrict_label.setStyleSheet("border:1px solid rgb(0, 255, 0); ")

        self.vol_label = QLabel()
        self.vol_label.setText(f"vol={round(PlayerConfigs.default_volume*100)}%")
        self.vol_label.setFixedHeight(15)
        self.vol_label.setStyleSheet("border:1px solid rgb(0, 0, 255); ")

        self.time_label_init_value = self.time_label.text()
        self.speed_label_init_value = self.speed_label.text()
        self.skip_label_init_value = self.skip_label.text()
        self.restrict_label_init_value = self.restrict_label.text()
        self.vol_label_init_value = self.vol_label.text()

        self.preview_widget = PreviewWidgetNew(self.update, self.get_preview_window_state(), self.get_preview_window_signal())
        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_widget)
        vbox.addWidget(self.slider)

        hbox = QHBoxLayout()
        hbox.addWidget(self.time_label)
        hbox.addWidget(self.speed_label)
        hbox.addWidget(self.skip_label)
        hbox.addWidget(self.restrict_label)
        hbox.addWidget(self.vol_label)
        hbox.addStretch()

        vbox.addLayout(hbox)

        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

        self.dialog = GoToFrameDialog(self)
        self.dialog.submit_slot.connect(self.dialog_box_done)

    def get_preview_window_state(self):
        return self.state.preview_window_output
    
    def get_preview_window_signal(self):
        return self.signals.preview_window_output
    
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
            cur_frame_no = self.preview_widget.get_cur_frame_no()
            frame_in_out = self.get_preview_window_state().frame_in_out
            in_frame = frame_in_out.get_resolved_in_frame()
            clip_total_frames = frame_in_out.get_no_of_frames(self.get_preview_window_state().total_frames) - 1 # starts from 0

            highlight_text_color = 'blue'
            fps = self.get_preview_window_state().fps
            abs_cur_time_str = build_time_str(*frames_to_time_components(cur_frame_no, fps))
            total_rel_frames = cur_frame_no - in_frame
            if total_rel_frames < 0:
                rel_cur_time_str = text_with_color('-'+build_time_str(*frames_to_time_components(total_rel_frames * -1, fps)), highlight_text_color)
            elif total_rel_frames > clip_total_frames:
                rel_cur_time_str = text_with_color(build_time_str(*frames_to_time_components(total_rel_frames, fps)), highlight_text_color)
            else:
                rel_cur_time_str = build_time_str(*frames_to_time_components(total_rel_frames, fps))
            total_time_str = build_time_str(*frames_to_time_components(clip_total_frames, fps))
            speed_txt = 'max' if self.get_preview_window_state().is_max_speed else 'normal'
            skip_txt = self.__build_skip_label_txt()

            self.time_label.setText(f'{abs_cur_time_str} ~ {rel_cur_time_str}/{total_time_str}')
            self.speed_label.setText(f'speed={speed_txt}')
            self.skip_label.setText(f'skip={skip_txt}')
            self.restrict_label.setText(f'restrict={self.get_preview_window_state().restrict_frame_interval}')
            self.vol_label.setText(f'vol={round(self.get_preview_window_state().volume*100)}%')
        else:
            self.time_label.setText(self.time_label_init_value)
            self.speed_label.setText(self.speed_label_init_value)
            self.skip_label.setText(self.skip_label_init_value)
            self.restrict_label.setText(self.restrict_label_init_value)
            self.vol_label.setText(self.vol_label_init_value)

    def update_slider(self):
        if self.preview_widget.cap is not None:
            if not self.slider.isEnabled:
                self.slider.setEnabled(True)
            
            start_frame = self.get_preview_window_state().cur_start_frame
            cur_total_frames = self.get_preview_window_state().cur_total_frames
            cur_frame_no = self.preview_widget.get_cur_frame_no()

            slider_value = int(round((cur_frame_no - start_frame) / cur_total_frames * self.slider.maximum()))

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
        pct = self.slider.slider_value_to_pct(value)
        pw_state = self.get_preview_window_state()
        cur_total_frames = pw_state.cur_total_frames
        start_frame = pw_state.cur_start_frame
        frame_no = int(round(pct * cur_total_frames)) + start_frame
        logging.debug(f'value changed to {value}, frame to {frame_no}, '
                      f'total_frames={pw_state.total_frames}')
        if not pw_state.restrict_frame_interval or pw_state.frame_in_out.contains_frame(frame_no, pw_state.total_frames):
            self.get_preview_window_signal().seek_slot.emit(frame_no, PositionType.ABSOLUTE)

    def _update_state_for_new_video(self, video_path: VideoPath, frame_in_out: FrameInOut):
        preview_window_state = self.get_preview_window_state()
        preview_window_state.video_path = video_path
        preview_window_state.frame_in_out = frame_in_out
        preview_window_state.restrict_frame_interval = True
        preview_window_state.fps = self.preview_widget.get_fps()
        preview_window_state.total_frames = self.preview_widget.get_total_frames()
        preview_window_state.current_frame_no = frame_in_out.get_resolved_in_frame()

        resolved_in_frame = frame_in_out.get_resolved_in_frame()
        resolved_out_frame = frame_in_out.get_resolved_out_frame(preview_window_state.total_frames)
        no_of_frames = preview_window_state.frame_in_out.get_no_of_frames(preview_window_state.total_frames)

        extra_frames_in_secs_config = self.state.app_config.extra_frames_in_secs_config
        extra_frames_config = int(round(extra_frames_in_secs_config * preview_window_state.fps))
        in_frame_in_secs = int(round(resolved_in_frame / preview_window_state.fps)) if preview_window_state.fps > 0 else 0
        leftover_frames = preview_window_state.total_frames - resolved_out_frame
        leftover_frames_in_secs = int(round(leftover_frames / preview_window_state.fps))
        extra_frames_on_left = extra_frames_config if in_frame_in_secs > extra_frames_in_secs_config else resolved_in_frame - 1
        extra_frames_on_right = extra_frames_config if leftover_frames_in_secs > extra_frames_in_secs_config else leftover_frames

        logging.debug(f'=== test1 no_of_frames {no_of_frames} left {extra_frames_on_left} right {extra_frames_on_right}')
        preview_window_state.cur_total_frames = no_of_frames + extra_frames_on_left + extra_frames_on_right
        preview_window_state.cur_start_frame = resolved_in_frame - extra_frames_on_left
        preview_window_state.cur_end_frame = resolved_out_frame + extra_frames_on_right

    def _update_state_for_blank_video(self, video_path: VideoPath):
        preview_window_state = self.get_preview_window_state()
        preview_window_state.video_path = video_path
        preview_window_state.frame_in_out = FrameInOut()
        preview_window_state.restrict_frame_interval = True
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
            name = video_path.file_name(include_ext=False)
            clip_idx = self.state.timeline.opened_clip_index + 1
            self.setWindowTitle(f'{self.base_title} - clip#{clip_idx} - {name}')
            self.slider.setDisabled(False)

        self.update()

    def toggle_play_pause(self, cmd: PlayCommand = PlayCommand.TOGGLE):
        if self.preview_widget.cap:
            self.preview_widget.exec_play_cmd(cmd)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        common_event_handling(event, self.signals, self.state)

        if is_key_press(event, Qt.Key_Space):
            self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.TOGGLE)
        elif is_key_press(event, Qt.Key_S):
            self.get_preview_window_signal().switch_speed_slot.emit()
        elif is_key_press(event, Qt.Key_I):
            self.get_preview_window_signal().in_frame_slot.emit(self.preview_widget.get_cur_frame_no())
            self.get_preview_window_signal().slider_update_slot.emit()
        elif is_key_with_modifiers(event, Qt.Key_I, shift=True):
            self.get_preview_window_signal().in_frame_slot.emit(None)
            self.get_preview_window_signal().slider_update_slot.emit()
        elif is_key_press(event, Qt.Key_O):
            self.get_preview_window_signal().out_frame_slot.emit(self.preview_widget.get_cur_frame_no())
            self.get_preview_window_signal().slider_update_slot.emit()
        elif is_key_with_modifiers(event, Qt.Key_O, shift=True):
            self.get_preview_window_signal().out_frame_slot.emit(None)
            self.get_preview_window_signal().slider_update_slot.emit()
        elif is_key_press(event, Qt.Key_Right):
            self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.PAUSE)
            self.get_preview_window_signal().seek_slot.emit(1, PositionType.RELATIVE)
        elif is_key_press(event, Qt.Key_BracketLeft):
            frame_in_out = self.get_preview_window_state().frame_in_out
            if frame_in_out.in_frame:
                self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.PAUSE)
                frame_diff = frame_in_out.in_frame - self.preview_widget.get_cur_frame_no()
                self.get_preview_window_signal().seek_slot.emit(frame_diff, PositionType.RELATIVE)
        elif is_key_press(event, Qt.Key_BracketRight):
            frame_in_out = self.get_preview_window_state().frame_in_out
            if frame_in_out.out_frame:
                self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.PAUSE)
                frame_diff = frame_in_out.out_frame - self.preview_widget.get_cur_frame_no()
                self.get_preview_window_signal().seek_slot.emit(frame_diff, PositionType.RELATIVE)
        elif is_key_with_modifiers(event, Qt.Key_Plus, numpad=True):
            self.get_preview_window_signal().update_skip_slot.emit(IncDec.INC)
        elif is_key_with_modifiers(event, Qt.Key_Minus, numpad=True):
            self.get_preview_window_signal().update_skip_slot.emit(IncDec.DEC)
        elif is_key_press(event, Qt.Key_F):
            self.get_preview_window_signal().switch_restrict_frame_slot.emit()
        elif is_key_press(event, Qt.Key_G):
            if self.preview_widget.cap is not None:
                self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.PAUSE)
                pw_state = self.get_preview_window_state()
                start_frame = pw_state.frame_in_out.get_resolved_in_frame() if pw_state.restrict_frame_interval else pw_state.cur_start_frame
                end_frame = pw_state.frame_in_out.get_resolved_out_frame(pw_state.total_frames) if pw_state.restrict_frame_interval else pw_state.cur_end_frame
                fps = self.get_preview_window_state().fps
                self.dialog.show_dialog(fps, self.preview_widget.get_cur_frame_no(), start_frame, end_frame)
        elif is_key_press(event, Qt.Key_V):
            if not self.get_preview_window_state().video_path.is_empty():
                cur_volume = round(self.get_preview_window_state().volume * 100)
                max_volume = round(PlayerConfigs.max_volume * 100)
                volume, ok = QInputDialog.getInt(self, 'Enter Volume', 'Volume (pct):', value=cur_volume, min=0, max=max_volume)
                if ok:
                    self.get_preview_window_signal().update_volume.emit(volume/100)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if is_key_press(event, Qt.Key_Left):
            self.get_preview_window_signal().play_cmd_slot.emit(PlayCommand.PAUSE)
            self.get_preview_window_signal().seek_slot.emit(-5, PositionType.RELATIVE)
        else:
            super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)

        frame_in_out = self.get_preview_window_state().frame_in_out
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
            left = int(round((frame_in_out.in_frame - start_frame) / cur_total_frames * self.width()))
            rect = QRect(left, 0, self.width(), self.height())
            painter.fillRect(rect, QColor(166, 166, 166, alpha=150))
        elif frame_in_out.out_frame is not None:
            right = int(round((frame_in_out.out_frame - start_frame) / cur_total_frames * self.width()))
            rect = QRect(0, 0, right, self.height())
            painter.fillRect(rect, QColor(166, 166, 166, alpha=150))

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.end()

    def wheelEvent(self, event: QWheelEvent) -> None:
        logging.debug('wheel event')
        # super().wheelEvent(e)
        if event.angleDelta().y() > 0:
            frame_diff = self.get_wheel_skip_time() * -1
        else:
            frame_diff = self.get_wheel_skip_time()

        self.signals.preview_window_output.seek_slot.emit(frame_diff, PositionType.RELATIVE)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.state.preview_window_output.restrict_frame_interval:
            new_val = self.pixel_pos_to_range_value(event.pos())

            pct = self.slider_value_to_pct(new_val)
            cur_total_frames = self.state.preview_window_output.cur_total_frames
            start_frame = self.state.preview_window_output.cur_start_frame
            frame_no = int(round(pct * cur_total_frames)) + start_frame
            if self.state.preview_window_output.frame_in_out.contains_frame(frame_no, self.state.preview_window_output.total_frames):
                logging.info(f'=== pct {pct} frame_no {frame_no}')
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        pct = self.slider_value_to_pct(self.value())
        cur_total_frames = self.state.preview_window_output.cur_total_frames
        start_frame = self.state.preview_window_output.cur_start_frame
        frame_no = int(round(pct * cur_total_frames)) + start_frame
        in_frame = self.state.preview_window_output.frame_in_out.get_resolved_in_frame()
        out_frame = self.state.preview_window_output.frame_in_out.get_resolved_out_frame(self.state.preview_window_output.total_frames)
        is_restricted = self.state.preview_window_output.restrict_frame_interval

        logging.debug(f'=== mouse release in_frame {out_frame} in_frame {out_frame} start_frame {start_frame} cur_total_frames {cur_total_frames} max {self.maximum()}')
        if in_frame > frame_no and is_restricted:
            self.signals.preview_window_output.seek_slot.emit(in_frame, PositionType.ABSOLUTE)
        elif out_frame < frame_no and is_restricted:
            self.signals.preview_window_output.seek_slot.emit(out_frame, PositionType.ABSOLUTE)
