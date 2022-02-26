import logging
import os

import cv2
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect, Qt, QTimer, QUrl
from PyQt5.QtGui import QPainter, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget

from goddo_player.app.app_constants import WINDOW_NAME_OUTPUT
from goddo_player.app.video_path import VideoPath
from goddo_player.utils.draw_utils import numpy_to_pixmap
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.signals import StateStoreSignals, PlayCommand
from goddo_player.app.state_store import StateStore
from goddo_player.utils.time_frame_utils import fps_to_num_millis


class PreviewWidget(QWidget):
    def __init__(self, on_update_fn, window_name):
        super().__init__()

        self.on_update_cb = on_update_fn
        self.state = StateStore()
        self.window_name = window_name
        self.signals = StateStoreSignals()

        self.cap = None

        self.setMinimumSize(640, 360)
        self.resize(self.minimumSize())
        self.setAcceptDrops(True)

        self.timer = QTimer(self)

        self.frame_pixmap = None
        self.restrict_frame_interval = True if window_name == WINDOW_NAME_OUTPUT else False

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

        preview_window_signals = self.signals.get_preview_window(self.window_name)
        preview_window_signals.switch_video_slot.emit(VideoPath(event.mimeData().urls()[0]), True)

    def switch_video(self, vid_path: VideoPath):
        preview_window_signals = self.signals.get_preview_window(self.window_name)

        if not vid_path.url().isEmpty():
            self.cap = cv2.VideoCapture(vid_path.str())

            fps = self.cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            preview_window_signals.update_file_details_slot.emit(fps, total_frames)

            self.timer.stop()
            self.timer.deleteLater()
            self.timer = QTimer(self)
            self.timer.setInterval(fps_to_num_millis(fps))
            self.timer.setTimerType(QtCore.Qt.PreciseTimer)
            self.timer.timeout.connect(self.update_frame_pixmap)
            # self.timer.start()
        else:
            self.cap = None
            preview_window_signals.update_file_details_slot.emit(0, 0)
            self.frame_pixmap = None

            self.timer.stop()
            self.timer.disconnect()

    def switch_speed(self):
        preview_window_state = self.state.get_preview_window(self.window_name)
        speed = fps_to_num_millis(preview_window_state.fps) if preview_window_state.is_max_speed else 1
        logging.info(f'switching speed from {self.timer.interval()} to {speed}')

        self.timer.stop()
        self.timer.deleteLater()
        self.timer = QTimer(self)
        self.timer.setInterval(speed)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.update_frame_pixmap)
        # self.timer.start()

        return speed

    def get_start_and_end_frames(self):
        preview_window_state = self.state.get_preview_window(self.window_name)
        total_frames = preview_window_state.total_frames
        in_frame = preview_window_state.frame_in_out.get_resolved_in_frame()
        out_frame = preview_window_state.frame_in_out.get_resolved_out_frame(total_frames)

        if self.restrict_frame_interval:
            return in_frame, out_frame
        else:
            return preview_window_state.cur_start_frame, preview_window_state.cur_end_frame

    def update_frame_pixmap(self, num_of_frames_to_advance=1):
        if self.cap:
            to_frame = self.get_cur_frame_no() + num_of_frames_to_advance
            start_frame, end_frame = self.get_start_and_end_frames()
            logging.debug(f'to_frame={to_frame} start_frame={start_frame} end_frame={end_frame}')

            if num_of_frames_to_advance == 0 and self.frame_pixmap:
                if self.frame_pixmap.width() != self.width() or self.frame_pixmap.height() != self.height():
                    self.frame_pixmap = self.frame_pixmap.scaled(self.width(), self.height())
            elif to_frame < start_frame or to_frame > end_frame:
                self.signals.preview_window_output.play_cmd_slot.emit(PlayCommand.PAUSE)
            elif 0 < num_of_frames_to_advance <= 10:
                logging.debug(f'num frames {num_of_frames_to_advance}')
                frame = None
                for i in range(num_of_frames_to_advance):
                    logging.debug('advancing frame')
                    frame = self.get_next_frame()
                scaled_frame = cv2.resize(frame, (self.width(), self.height()),
                                          interpolation=cv2.INTER_AREA)
                self.frame_pixmap = numpy_to_pixmap(scaled_frame)
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
