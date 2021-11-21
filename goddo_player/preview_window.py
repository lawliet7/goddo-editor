import logging
import os
import threading

import cv2
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import QPainter, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget

from goddo_player.draw_utils import numpy_to_pixmap
from goddo_player.state_store import StateStoreSignals


class PreviewWindow(QWidget):
    supported_video_ext = ['.mp4', '.wmv', '.mkv']

    def __init__(self):
        super().__init__()
        self.base_title = '天使女捜査官'
        self.setWindowTitle(self.base_title)

        self.signals = StateStoreSignals()

        self.cap = None

        self.setBaseSize(640, 360)
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
            if ext in self.supported_video_ext:
                event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        logging.info(f'drop {event.mimeData().urls()}')

        self.signals.update_preview_file_slot.emit(event.mimeData().urls()[0])

    def switch_video(self, url: 'QUrl'):
        self.cap = cv2.VideoCapture(url.path())

        self.timer.stop()
        self.timer.deleteLater()
        self.timer = QTimer(self)
        self.timer.setInterval(1)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(lambda: self.update())
        self.timer.start()

        name, _ = os.path.splitext(url.fileName())
        self.setWindowTitle(self.base_title + ' - ' + name)

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.signals.update_preview_file_details_slot.emit(fps, total_frames)

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
        else:
            painter.fillRect(QRect(0, 0, self.geometry().width(), self.geometry().height()), Qt.black)

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.end()

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
