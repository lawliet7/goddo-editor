import logging
import os
import threading

import cv2
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect, Qt, QTimer, QUrl
from PyQt5.QtGui import QPainter, QDragEnterEvent, QDropEvent, QKeyEvent
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QSlider, QLabel

from goddo_player.draw_utils import numpy_to_pixmap
from goddo_player.player_configs import PlayerConfigs
from goddo_player.state_store import StateStoreSignals, StateStore
from goddo_player.time_frame_utils import build_time_str, frames_to_time_components


class PreviewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.base_title = '天使女捜査官'
        self.setWindowTitle(self.base_title)

        self.state = StateStore()
        self.signals = StateStoreSignals()

        self.cap = None

        # self.setMinimumSize(640, 360)
        # self.resize(self.minimumSize())
        self.setAcceptDrops(True)

        self.timer = QTimer(self)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setRange(0, 100)
        self.slider.valueChanged.connect(self.on_value_changed)

        # p = self.palette()
        # p.setColor(self.backgroundRole(), Qt.black)
        # self.setPalette(p)
        # self.setAutoFillBackground(True)

        self.label = QLabel()
        self.label.setText("you suck")

        self.preview_widget = PreviewWidget(self.__on_update_pos)
        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_widget)
        vbox.addWidget(self.slider)
        vbox.addWidget(self.label)

        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    def __on_update_pos(self, cur_frame_no: int, frame):
        total_frames = self.state.preview_window.total_frames
        pos = int(round(cur_frame_no / total_frames * 100))
        self.slider.setValue(pos)

        fps = self.state.preview_window.fps
        cur_time_str = build_time_str(*frames_to_time_components(cur_frame_no, fps))
        total_time_str = build_time_str(*frames_to_time_components(total_frames, fps))
        self.label.setText(f'{cur_time_str}/{total_time_str}')

    def on_value_changed(self, value):
        print(f'value changed to {value}')

    def switch_video(self, url: 'QUrl'):
        self.preview_widget.switch_video(url)

        name, _ = os.path.splitext(url.fileName())
        self.setWindowTitle(self.base_title + ' - ' + name)

    def toggle_play_pause(self):
        self.preview_widget.toggle_play_pause()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            url = QUrl.fromLocalFile(os.path.abspath(os.path.join('..', 'saves', 'a.json')))
            self.state_signals.save_slot.emit(url)
        elif event.key() == Qt.Key_Space:
            self.toggle_play_pause()
        # elif event.key() == Qt.Key_K:
        #     self.slider.setValue(10)
        else:
            super().keyPressEvent(event)


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

        self.timer.stop()
        self.timer.deleteLater()
        self.timer = QTimer(self)
        self.timer.setInterval(1)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(lambda: self.update())
        # self.timer.start()

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.signals.update_preview_file_details_slot.emit(fps, total_frames)
        cur_time_str = build_time_str(*frames_to_time_components(0, fps))


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

    def toggle_play_pause(self):
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
