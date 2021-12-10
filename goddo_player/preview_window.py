import logging
import os
import threading

import cv2
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect, Qt, QTimer, QUrl, QMimeData
from PyQt5.QtGui import QPainter, QDragEnterEvent, QDropEvent, QKeyEvent, QPaintEvent, QColor, QMouseEvent, QDrag
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel

from goddo_player.click_slider import ClickSlider
from goddo_player.draw_utils import numpy_to_pixmap
from goddo_player.player_configs import PlayerConfigs
from goddo_player.signals import StateStoreSignals, PlayCommand
from goddo_player.state_store import StateStore
from goddo_player.time_frame_utils import build_time_str, frames_to_time_components, num_frames_to_num_millis


class PreviewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.base_title = '天使美女捜査官'
        self.setWindowTitle(self.base_title)

        self.state = StateStore()
        self.signals = StateStoreSignals()

        self.cap = None

        # self.setMinimumSize(640, 360)
        # self.resize(self.minimumSize())
        self.setAcceptDrops(True)

        self.slider = FrameInOutSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setRange(0, 200)
        self.slider.valueChanged.connect(self.on_value_changed)
        self.slider.setFixedHeight(20)

        # p = self.palette()
        # p.setColor(self.backgroundRole(), Qt.black)
        # self.setPalette(p)
        # self.setAutoFillBackground(True)

        self.label = QLabel()
        self.label.setText("you suck")
        self.label.setFixedHeight(15)

        self.preview_widget = PreviewWidget(self.__on_update_pos)
        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_widget)
        vbox.addWidget(self.slider)
        vbox.addWidget(self.label)

        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    def __on_update_pos(self, cur_frame_no: int, frame):
        total_frames = self.state.preview_window.total_frames
        pos = self.slider.pct_to_slider_value(cur_frame_no / total_frames)
        self.slider.blockSignals(True)
        self.slider.setValue(pos)
        self.slider.blockSignals(False)

        fps = self.state.preview_window.fps
        cur_time_str = build_time_str(*frames_to_time_components(cur_frame_no, fps))
        total_time_str = build_time_str(*frames_to_time_components(total_frames, fps))
        speed = 'max' if self.preview_widget.timer.interval() == 1 else 'normal'
        self.label.setText(f'{cur_time_str}/{total_time_str}  speed={speed}')

    def on_value_changed(self, value):
        frame_no = int(round(self.slider.slider_value_to_pct(value) * self.state.preview_window.total_frames))
        logging.info(f'value changed to {value}, frame to {frame_no}, '
                     f'total_frames={self.state.preview_window.total_frames}')
        self.preview_widget.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no-1)
        if not self.preview_widget.timer.isActive():
            self.update()

    def switch_video(self, url: 'QUrl'):
        self.preview_widget.switch_video(url)

        name, _ = os.path.splitext(url.fileName())
        self.setWindowTitle(self.base_title + ' - ' + name)

    def toggle_play_pause(self, cmd: PlayCommand = PlayCommand.TOGGLE):
        self.preview_widget.exec_play_cmd(cmd)

    def update_next_frame(self):
        self.update()

    def update_prev_frame(self, num_of_frames=1):
        target_frame_no = self.preview_widget.get_cur_frame_no() - num_of_frames - 1
        self.preview_widget.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_no)
        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            url = QUrl.fromLocalFile(os.path.abspath(os.path.join('..', 'saves', 'a.json')))
            self.signals.save_slot.emit(url)
        elif event.key() == Qt.Key_Space:
            self.signals.preview_window_play_cmd_slot.emit(PlayCommand.TOGGLE)
        elif event.key() == Qt.Key_S:
            self.preview_widget.switch_speed()
        elif event.key() == Qt.Key_I:
            self.signals.preview_video_in_frame_slot.emit(self.preview_widget.get_cur_frame_no())
            self.signals.preview_video_slider_update_slot.emit()
        elif event.modifiers() == Qt.ShiftModifier and event.key() == Qt.Key_I:
            self.signals.preview_video_in_frame_slot.emit(None)
            self.signals.preview_video_slider_update_slot.emit()
        elif event.key() == Qt.Key_O:
            self.signals.preview_video_out_frame_slot.emit(self.preview_widget.get_cur_frame_no())
            self.signals.preview_video_slider_update_slot.emit()
        elif event.modifiers() == Qt.ShiftModifier and event.key() == Qt.Key_O:
            self.signals.preview_video_out_frame_slot.emit(None)
            self.signals.preview_video_slider_update_slot.emit()
        elif event.key() == Qt.Key_Right:
            self.signals.preview_window_play_cmd_slot.emit(PlayCommand.PAUSE)
            self.update_next_frame()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Left:
            self.signals.preview_window_play_cmd_slot.emit(PlayCommand.PAUSE)
            self.update_prev_frame(5)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)

        frame_in_out = self.state.preview_window.frame_in_out
        if frame_in_out.in_frame is not None or frame_in_out.out_frame is not None:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText('source')
            drag.setMimeData(mime_data)
            drag.exec()


class PreviewWidget(QWidget):
    def __init__(self, on_update_fn):
        super().__init__()

        self.on_update_cb = on_update_fn
        self.state = StateStore()
        self.signals = StateStoreSignals()

        self.cap = None

        self.setMinimumSize(640, 360)
        self.resize(self.minimumSize())
        self.setAcceptDrops(True)

        self.timer = QTimer(self)

    def get_cur_frame_no(self):
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def get_next_frame(self, specific_frame=None):
        if specific_frame:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, specific_frame)

        if self.cap.grab():
            flag, frame = self.cap.retrieve()
            if flag:
                return frame

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        urls = event.mimeData().urls()

        if len(urls) == 1:
            filename = urls[0].fileName()
            name, ext = os.path.splitext(filename)
            if ext in PlayerConfigs.supported_video_exts:
                event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        logging.info(f'drop {event.mimeData().urls()}')

        self.signals.switch_preview_video_slot.emit(event.mimeData().urls()[0], True)

    def switch_video(self, url: 'QUrl'):
        self.cap = cv2.VideoCapture(url.path())

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.signals.update_preview_file_details_slot.emit(fps, total_frames)

        self.timer.stop()
        self.timer.deleteLater()
        self.timer = QTimer(self)
        self.timer.setInterval(num_frames_to_num_millis(fps))
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(lambda: self.update())
        # self.timer.start()

    def switch_speed(self):
        speed = 1 if self.timer.interval() != 1 else num_frames_to_num_millis(self.state.preview_window.fps)
        logging.info(f'switching speed from {self.timer.interval()} to {speed}')

        self.timer.stop()
        self.timer.deleteLater()
        self.timer = QTimer(self)
        self.timer.setInterval(speed)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(lambda: self.update())
        self.timer.start()

    def paintEvent(self, paint_event: QtGui.QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)

        pen = painter.pen()
        brush = painter.brush()

        if self.cap:
            scaled_frame = cv2.resize(self.get_next_frame(), (self.width(), self.height()), interpolation=cv2.INTER_AREA)
            pixmap = numpy_to_pixmap(scaled_frame)
            painter.drawPixmap(0, 0, pixmap)

            cur_frame_no = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.on_update_cb(cur_frame_no, scaled_frame)

        else:
            painter.fillRect(QRect(0, 0, self.geometry().width(), self.geometry().height()), Qt.black)

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.end()

    def exec_play_cmd(self, play_cmd: PlayCommand):
        if play_cmd is PlayCommand.PLAY:
            self.timer.start()
        elif play_cmd is PlayCommand.PAUSE:
            self.timer.stop()
        else:
            if self.timer.isActive():
                self.timer.stop()
            else:
                self.timer.start()

    def update_frame(self, frame_no=-1):
        logging.debug("[{}] updating frame".format(threading.get_ident()))

        # if not self.is_playing and frame_no == -1:
        #     pass
        # elif not self.video_player.is_video_done() or (self.video_player.is_video_done() and frame_no > -1):
        #     new_time = get_perf_counter_as_millis()
        #     cur_frame = self.video_player.get_current_frame()
        #     target_frame = None
        #     if frame_no < 0:
        #         logging.debug("in frame < 0, {} - {} = {}".format(new_time, self.current_time,
        #                                                           new_time - self.current_time))
        #         time_diff = new_time - self.current_time
        #         frame_diff = convert_to_int(time_diff/self.fps_as_ms)
        #         logging.debug('diffs {} {}'.format(time_diff, frame_diff))
        #         frame_diff = 1  # this might be slightly slower sometimes but at least it's in sync
        #         if frame_diff > 0:
        #             target_frame = self.video_player.skip_until_frame(frame_diff)
        #         self.audio_player.emit_play_audio_signal(frame_diff, not self.is_playing)
        #     elif frame_no > cur_frame and frame_no - cur_frame < 10:
        #         frame_diff = frame_no > cur_frame
        #         if frame_diff > 0:
        #             target_frame = self.video_player.skip_until_frame(frame_diff)
        #             self.audio_player.emit_play_audio_signal(frame_diff, not self.is_playing)
        #     else:
        #         target_frame = self.video_player.get_next_frame(frame_no)
        #         self.audio_player.emit_go_to_audio_signal(frame_no)
        #     # target_frame = get_next_frame(self.cap)
        #
        #     if target_frame is not None:
        #         new_dim = get_resize_dim_keep_aspect(*self.video_player.get_video_dimensions(), self.base_width)
        #         scaled_frame = cv2.resize(target_frame, new_dim, interpolation=cv2.INTER_AREA)
        #         self.pixmap = numpy_to_pixmap(scaled_frame)
        #         self.current_time = new_time
        #         logging.debug("update audio pos")
        #     else:
        #         logging.debug("skipped advancing frame")

        self.update()


class FrameInOutSlider(ClickSlider):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = StateStore()
        self.signals = StateStoreSignals()

        self.signals.preview_video_slider_update_slot.connect(lambda: self.update())

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
