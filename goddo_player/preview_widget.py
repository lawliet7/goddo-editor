import logging
import os
import threading

import cv2
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect, Qt, QTimer, QUrl
from PyQt5.QtGui import QPainter, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget

from goddo_player.draw_utils import numpy_to_pixmap
from goddo_player.player_configs import PlayerConfigs
from goddo_player.signals import StateStoreSignals, PlayCommand
from goddo_player.state_store import StateStore
from goddo_player.time_frame_utils import num_frames_to_num_millis


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

        self.frame_pixmap = None

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

        self.signals.preview_window.switch_video_slot.emit(event.mimeData().urls()[0], True)

    def switch_video(self, url: 'QUrl'):
        self.cap = cv2.VideoCapture(url.path())

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.signals.preview_window.update_file_details_slot.emit(fps, total_frames)

        self.timer.stop()
        self.timer.deleteLater()
        self.timer = QTimer(self)
        self.timer.setInterval(num_frames_to_num_millis(fps))
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.update_frame_pixmap)
        # self.timer.start()

    def switch_speed(self):
        speed = num_frames_to_num_millis(self.state.preview_window.fps) if self.state.preview_window.is_max_speed else 1
        logging.info(f'switching speed from {self.timer.interval()} to {speed}')

        self.timer.stop()
        self.timer.deleteLater()
        self.timer = QTimer(self)
        self.timer.setInterval(speed)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.update_frame_pixmap)
        # self.timer.start()

        return speed

    def update_frame_pixmap(self, num_of_frames_to_advance=1):
        if self.cap:
            if 0 < num_of_frames_to_advance <= 10:
                logging.info(f'num frames {num_of_frames_to_advance}')
                frame = None
                for i in range(num_of_frames_to_advance):
                    logging.info('advancing frame')
                    frame = self.get_next_frame()
                scaled_frame = cv2.resize(frame, (self.width(), self.height()),
                                          interpolation=cv2.INTER_AREA)
                self.frame_pixmap = numpy_to_pixmap(scaled_frame)
            elif num_of_frames_to_advance == 0 and self.frame_pixmap:
                self.frame_pixmap = self.frame_pixmap.scaled(self.width(), self.height())
            else:
                target_frame_no = max(self.get_cur_frame_no() + num_of_frames_to_advance - 1, 0)
                scaled_frame = cv2.resize(self.get_next_frame(target_frame_no), (self.width(), self.height()),
                                          interpolation=cv2.INTER_AREA)
                self.frame_pixmap = numpy_to_pixmap(scaled_frame)

            cur_frame_no = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.on_update_cb(cur_frame_no, self.frame_pixmap)

        self.update()

    def paintEvent(self, paint_event: QtGui.QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)

        pen = painter.pen()
        brush = painter.brush()

        if self.frame_pixmap:
            # scaled_frame = cv2.resize(self.get_next_frame(), (self.width(), self.height()), interpolation=cv2.INTER_AREA)
            # pixmap = numpy_to_pixmap(scaled_frame)
            painter.drawPixmap(0, 0, self.frame_pixmap)
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