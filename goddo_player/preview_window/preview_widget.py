import logging
import os

import cv2
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import QPainter, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget

from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.signals import PlayCommand, StateStoreSignals
from goddo_player.utils.enums import PositionType
from goddo_player.utils.video_path import VideoPath
from goddo_player.utils.draw_utils import numpy_to_pixmap
from goddo_player.utils.time_frame_utils import fps_to_num_millis
from goddo_player.widgets.audio_widget import AudioPlayer2
from goddo_player.app.app_constants import WINDOW_NAME_SOURCE, WINDOW_NAME_OUTPUT


class PreviewWidgetNew(QWidget):
    def __init__(self, pw_update_fn, pw_state, pw_signal):
        super().__init__()

        self.pw_update_fn = pw_update_fn
        self.pw_state = pw_state
        self.pw_signal = pw_signal
        self.signals = StateStoreSignals()

        self.cap = None
        self.audio_player = AudioPlayer2(False if pw_state.name == WINDOW_NAME_SOURCE else True)

        self.setMinimumSize(640, 360)
        self.resize(self.minimumSize())
        self.setAcceptDrops(True)

        self.timer = QTimer(self)

        self.frame_pixmap = None

    def get_cur_frame_no(self):
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) if self.cap else 0

    def set_cap_pos(self, frame_no):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)

    def grab_next_frame(self, convert_to_pixmap=True):
        if self.cap.grab():
            flag, frame = self.cap.retrieve()
            if flag:
                if convert_to_pixmap:
                    scaled_frame = cv2.resize(frame, (self.width(), self.height()), interpolation=cv2.INTER_AREA)
                    return numpy_to_pixmap(scaled_frame)
                else:
                    return frame

    def get_fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS) if self.cap else 0

    def get_total_frames(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) if self.cap else 0

    def switch_video(self, video_path: VideoPath):
        if not video_path.is_empty():
            self.cap = cv2.VideoCapture(video_path.str())

            if self.timer:
                self.timer.stop()
                self.timer.deleteLater()

            self.timer = QTimer(self)
            self.timer.setInterval(fps_to_num_millis(self.get_fps()))
            self.timer.setTimerType(QtCore.Qt.PreciseTimer)
            self.timer.timeout.connect(self.play_callback)
            # self.timer.start()
        else:
            self.cap = None
            self.pw_signal.update_file_details_slot.emit(0, 0)
            self.frame_pixmap = None

            if self.timer:
                self.timer.stop()
                self.timer.deleteLater()
                self.timer = None
    
    def play_callback(self):
        cur_frame_no = self.get_cur_frame_no()
        frame_no = self.go_to_frame(1, PositionType.RELATIVE)
        logging.debug(f'callback {frame_no}')
        
        _, end_frame = self.get_start_and_end_frames()

        # if cur_frame_no and frame_no is same then opencv is not able to advance to next frame 
        # so mind as well pause to save on processing power
        if frame_no == end_frame or cur_frame_no == frame_no:
            logging.info(f'pausing since frame no {frame_no} has reach the end frame {end_frame}')
            self.pw_signal.play_cmd_slot.emit(PlayCommand.PAUSE)

        self.pw_update_fn()

    def switch_speed(self):
        speed = fps_to_num_millis(self.pw_state.fps) if self.pw_state.is_max_speed else 1
        logging.info(f'switching speed from {self.timer.interval() if self.timer else 0} to {speed}')

        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()

        self.timer = QTimer(self)
        self.timer.setInterval(speed)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.play_callback)
        # self.timer.start()

        return speed

    def get_start_and_end_frames(self):
        total_frames = self.pw_state.total_frames
        in_frame = self.pw_state.frame_in_out.get_resolved_in_frame()
        out_frame = self.pw_state.frame_in_out.get_resolved_out_frame(total_frames)

        if self.pw_state.restrict_frame_interval:
            return in_frame, out_frame
        else:
            return self.pw_state.cur_start_frame, self.pw_state.cur_end_frame

    def go_to_frame(self, frame_no: int, pos_type: PositionType):
        if self.cap:
            cur_frame_no = self.get_cur_frame_no()
            target_frame_no = frame_no if pos_type is PositionType.ABSOLUTE else cur_frame_no + frame_no
            start_frame, end_frame = self.get_start_and_end_frames()
            # logging.debug(f'to_frame={target_frame_no} start_frame={start_frame} end_frame={end_frame}')

            if cur_frame_no == target_frame_no or \
                target_frame_no <= start_frame == cur_frame_no or \
                    cur_frame_no == end_frame <= target_frame_no:
                if self.frame_pixmap and (self.frame_pixmap.width() != self.width() or self.frame_pixmap.height() != self.height()):
                    self.frame_pixmap = self.frame_pixmap.scaled(self.width(), self.height())
            elif target_frame_no <= start_frame:
                self.set_cap_pos(start_frame - 1)
                self.frame_pixmap = self.grab_next_frame()
            elif target_frame_no >= end_frame:
                if 0 < (end_frame - cur_frame_no - 1) <= 10:
                    for _ in range(end_frame - cur_frame_no - 1):
                        self.grab_next_frame(convert_to_pixmap=False)
                elif cur_frame_no != (end_frame - 1):
                    self.set_cap_pos(end_frame - 1)
                self.frame_pixmap = self.grab_next_frame()
            elif 0 < (target_frame_no - cur_frame_no) <= 10:
                for _ in range(target_frame_no - cur_frame_no - 1):
                    self.grab_next_frame(convert_to_pixmap=False)
                self.frame_pixmap = self.grab_next_frame()
                self.audio_player.worker.signals.play_audio.emit(1, False)
            else:
                if cur_frame_no != (end_frame - 1):
                    self.set_cap_pos(target_frame_no - 1)
                self.frame_pixmap = self.grab_next_frame()

            cur_frame_no = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

            self.update()

            return cur_frame_no
        else:
            return 0

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
            if self.is_playing():
                self.timer.stop()
            else:
                self.timer.start()

    def is_playing(self):
        return self.timer and self.timer.isActive()
