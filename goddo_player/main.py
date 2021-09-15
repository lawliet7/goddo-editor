import argparse
import logging
import os
import pickle
import sys
import threading
from io import BytesIO

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, QEvent, QMimeData
from PyQt5.QtGui import QMouseEvent, QOpenGLWindow, QSurfaceFormat, QKeyEvent, QFont, QCloseEvent, QDrag

from goddo_player.AudioPlayer import AudioPlayer
from goddo_player.DragAndDrop import VideoClipDragItem
from goddo_player.VideoPlayer import VideoPlayer
from goddo_player.draw_utils import *
from goddo_player.save_state import State
from goddo_player.time_frame_utils import *
from goddo_player.timeline_window import TimelineWindow
from goddo_player.volume import VolumeControl
from goddo_player.window_util import *
from number_utils import convert_to_int
from theme import Theme


def print_all_populated_openv_attrs(cap):
    for attr in [x for x in dir(cv2) if x.startswith('CAP_PROP_')]:
        attr_value = cap.get(getattr(cv2, attr))
        if attr_value != 0:
            logging.info('{} = {}'.format(attr, attr_value))


def scale_image(img, scale):
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    dim = (width, height)
    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)


class MainLoopUpdateSignals(QObject):
    update_frame = pyqtSignal(int)


class AdhocUpdateSignals(QObject):
    update_frame = pyqtSignal(int)


class MainWindow(QOpenGLWindow):
    def __init__(self, state: State, initial_offset=None):
        super().__init__()

        self.base_width = 1024
        self.state = state

        self.video_player = VideoPlayer(state)
        print_all_populated_openv_attrs(self.video_player.cap)
        self.fps = self.video_player.fps
        self.fps_as_ms = num_frames_to_num_millis(self.fps)
        self.pixmap = None

        self.audio_player = AudioPlayer(state, self.fps)
        self.current_time = get_perf_counter_as_millis()

        self.slider_circle_radius = 5
        self.slider_rect: QRect = None

        self.main_signals = MainLoopUpdateSignals()
        self.main_signals.update_frame.connect(self.update_frame)

        self.adhoc_signals = AdhocUpdateSignals()
        self.adhoc_signals.update_frame.connect(self.update_frame)

        self.timer = QTimer(self)
        self.timer.setInterval(self.fps_as_ms+1)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.emit_update_frame_signal)
        self.timer.start()

        self.is_mouse_over = False
        self.is_playing = True

        self.theme = Theme()

        self.volume_control_widget = VolumeControl(self.geometry, self.update_volume, self.manual_update_ui,
                                                   color=self.theme.color.controls)

        self.child_windows = []

        # if initial_offset:
        #     self.emit_update_frame_signal(initial_offset)

    def update_volume(self, volume):
        self.audio_player.volume = volume

    def manual_update_ui(self):
        if not self.is_playing:
            self.update()

    def paint_with_painter(self, fn: Callable[[QPainter], None], antialias=True):
        paint_helper(self, fn, antialias=antialias)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Space:
            self.is_playing = not self.is_playing
        elif event.key() == Qt.Key_I:
            self.state.source['in_frame'] = self.video_player.get_current_frame()
            if self.state.source['out_frame'] and self.state.source['in_frame'] > self.state.source['out_frame']:
                self.state.source['out_frame'] = None
        elif event.key() == Qt.Key_O:
            self.state.source['out_frame'] = self.video_player.get_current_frame()
            if self.state.source['in_frame'] and self.state.source['out_frame'] < self.state.source['in_frame']:
                self.state.source['in_frame'] = None
        elif event.key() == Qt.Key_Left:
            if self.is_playing:
                self.is_playing = not self.is_playing

            self.main_signals.blockSignals(True)
            to_frame = max(0, self.video_player.get_current_frame()-2)
            self.adhoc_signals.update_frame.emit(to_frame)
            print(f"updating to {to_frame}")
            self.main_signals.blockSignals(False)
        elif event.key() == Qt.Key_Right:
            if self.is_playing:
                self.is_playing = not self.is_playing

            self.main_signals.blockSignals(True)
            to_frame = min(self.video_player.total_frames, self.video_player.get_current_frame()+1)
            self.adhoc_signals.update_frame.emit(to_frame)
            print(f"updating to {to_frame}")
            self.main_signals.blockSignals(False)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            print("save it")
            self.is_playing = False
            self.state.save(self)
        else:
            super().keyPressEvent(event)

    @staticmethod
    def create_default_surface():
        fmt = QSurfaceFormat()
        fmt.setSamples(4)
        QSurfaceFormat.setDefaultFormat(fmt)

    def initializeGL(self) -> None:
        super().initializeGL()

        self.create_default_surface()

        new_dim = get_resize_dim_keep_aspect(*self.video_player.get_video_dimensions(), self.base_width)
        self.resize(*new_dim)
        self.slider_rect = self.get_slider_rect()

        timeline_window = TimelineWindow(self)
        timeline_window.show()
        self.child_windows.append(timeline_window)

        # draw text seems to need to be 'warmed up' to run quickly
        self.paint_with_painter(lambda painter: painter.drawText(QPoint(0, 0), "x"))

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QMouseEvent.Enter:
            return True
        elif event.type() == QMouseEvent.Leave:
            return True
        elif event.type() == QCloseEvent.Close:
            return True
        return super().eventFilter(obj, event)

    def event(self, event: QtCore.QEvent) -> bool:
        if dir(self).__contains__('volume_control_widget'):
            # print('in volume control event')
            self.volume_control_widget.event(event)

        if event.type() == QMouseEvent.Enter:
            logging.debug('mouse enter')
            self.requestActivate()
            self.is_mouse_over = True
            return True
        elif event.type() == QMouseEvent.Leave:
            logging.debug('mouse leave')
            self.is_mouse_over = False
            return True
        elif event.type() == QCloseEvent.Close:
            QApplication.exit(0)
            return True
        return super().event(event)

    def paintGL(self) -> None:
        if self.pixmap is not None:
            self.paint_with_painter(lambda painter: painter.drawPixmap(0, 0, self.pixmap))

    def paintOverGL(self) -> None:
        logging.debug(self.is_mouse_over)
        if self.is_mouse_over:
            self.paint_with_painter(self.draw_in_out_box)
            self.paint_with_painter(self.draw_seek_bar)
            self.paint_with_painter(self.draw_timestamp)
            self.paint_with_painter(self.draw_play_button)
            self.paint_with_painter(self.volume_control_widget.paint)

    def get_slider_rect(self):
        distance = 100
        height_of_slider_rect = 30
        width = self.geometry().width()
        height = self.geometry().height()
        return QRect(0, height - distance, width, height_of_slider_rect)

    def update_frame(self, frame_no=-1):
        logging.debug("[{}] updating frame".format(threading.get_ident()))
        # self.main_signals.blockSignals(True)
        # print('updating frame {}'.format(frame_no))
        if not self.is_playing and frame_no == -1:
            pass
        elif not self.video_player.is_video_done() or (self.video_player.is_video_done() and frame_no > -1):
            new_time = get_perf_counter_as_millis()
            cur_frame = self.video_player.get_current_frame()
            target_frame = None
            if frame_no < 0:
                logging.debug("in frame < 0, {} - {} = {}".format(new_time, self.current_time,
                                                                  new_time - self.current_time))
                time_diff = new_time - self.current_time
                frame_diff = convert_to_int(time_diff/self.fps_as_ms)
                logging.debug('diffs {} {}'.format(time_diff, frame_diff))
                frame_diff = 1  # this might be slightly slower sometimes but at least it's in sync
                if frame_diff > 0:
                    target_frame = self.video_player.skip_until_frame(frame_diff)
                self.audio_player.emit_play_audio_signal(frame_diff, not self.is_playing)
            elif frame_no > cur_frame and frame_no - cur_frame < 10:
                frame_diff = frame_no > cur_frame
                if frame_diff > 0:
                    target_frame = self.video_player.skip_until_frame(frame_diff)
                    self.audio_player.emit_play_audio_signal(frame_diff, not self.is_playing)
            else:
                target_frame = self.video_player.get_next_frame(frame_no)
                self.audio_player.emit_go_to_audio_signal(frame_no)
            # target_frame = get_next_frame(self.cap)

            if target_frame is not None:
                new_dim = get_resize_dim_keep_aspect(*self.video_player.get_video_dimensions(), self.base_width)
                scaled_frame = cv2.resize(target_frame, new_dim, interpolation=cv2.INTER_AREA)
                self.pixmap = numpy_to_pixmap(scaled_frame)
                self.current_time = new_time
                logging.debug("update audio pos")
            else:
                logging.debug("skipped advancing frame")

        self.update()

        # self.main_signals.blockSignals(False)

    def draw_in_out_box(self, painter):
        if self.state.source['in_frame'] is not None or self.state.source['out_frame'] is not None:
            left = self.slider_rect.left()
            if self.state.source['in_frame']:
                in_pct_done = self.state.source['in_frame'] / self.video_player.total_frames
                left = convert_to_int(in_pct_done*self.slider_rect.width()+self.slider_rect.left())

            right = self.slider_rect.right()
            if self.state.source['out_frame']:
                out_pct_done = self.state.source['out_frame'] / self.video_player.total_frames
                right = convert_to_int(out_pct_done * self.slider_rect.width() + self.slider_rect.left())

            painter.setPen(create_pen(color=self.theme.color.half_opacity_gray))
            painter.setBrush(QBrush(self.theme.color.half_opacity_gray, Qt.SolidPattern))
            painter.drawRect(QRect(QPoint(left, self.slider_rect.top()), QPoint(right, self.slider_rect.bottom())))

    def draw_seek_bar(self, painter: QPainter):
        pct_done = self.video_player.get_current_frame() / self.video_player.total_frames
        draw_slider(self.slider_rect, painter, self.theme, pct_done)

    def draw_timestamp(self, painter):
        y_of_elapsed_time = int(self.slider_rect.bottom() - 10 + self.slider_circle_radius + 10)
        painter.setPen(create_pen())

        font = QFont()
        font.setFamily("Helvetica [Cronyx]")
        painter.setFont(font)

        cur_frames = self.video_player.get_current_frame()
        painter.drawText(QPoint(5, y_of_elapsed_time), format_time(*frames_to_time_components(cur_frames, self.fps)))

        total_frames = self.video_player.total_frames
        painter.drawText(QPoint(self.slider_rect.width() - 60, y_of_elapsed_time),
                         format_time(*frames_to_time_components(total_frames, self.fps)))

    def draw_play_button(self, painter):
        slider_bottom = self.slider_rect.bottom()
        rect = QRect(0, slider_bottom, self.slider_rect.width(), self.geometry().height() - slider_bottom-5)
        draw_play_button(painter, rect, self.is_playing, color=self.theme.color.controls)

    def emit_update_frame_signal(self, target_frame=-1):
        self.main_signals.update_frame.emit(target_frame)

    def mousePressEvent(self, event: QMouseEvent):
        logging.debug(event.pos())
        logging.debug(self.slider_rect.contains(event.pos()))

        if self.slider_rect.contains(event.pos()):
            pct = (event.pos().x() - self.slider_rect.left()) / self.slider_rect.width()
            target_frame = convert_to_int(pct*self.video_player.total_frames)
            logging.debug('target frame: {}, {}'.format(pct, target_frame))

            self.main_signals.blockSignals(True)
            self.adhoc_signals.update_frame.emit(target_frame)
            self.main_signals.blockSignals(False)
        elif event.pos().y() < self.slider_rect.top():
            if self.state.source['in_frame'] and self.state.source['out_frame']:
                drag = QDrag(self)
                mime_data = QMimeData()

                data = VideoClipDragItem(self.state.source['in_frame'], self.state.source['out_frame'],
                                         self.video_player.video_path,
                                         self.video_player.fps)
                bytes_output = BytesIO()
                pickle.dump(data, bytes_output)

                mime_data.setData("custom", bytes_output.getvalue())
                print(mime_data)
                drag.setMimeData(mime_data)
                drag.exec()


def convert_to_log_level(log_level_str: str):
    if log_level_str:
        return logging.getLevelName(log_level_str.upper())
    else:
        return None


def get_resize_dim_keep_aspect(original_width: int, original_height: int, target_width: int):
    if original_width > target_width:
        new_width = target_width
        adjusted_height = convert_to_int(new_width * original_height / original_width)
    else:
        new_width = int(original_width)
        adjusted_height = int(original_height)

    return new_width, adjusted_height


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Goddo Serenade's video editor")
    parser.add_argument('video', help='video file')
    parser.add_argument('--offset', type=int, help='offset frame to start from')
    parser.add_argument('--save', help='save file')

    args = parser.parse_args()
    print(args)

    log_level = convert_to_log_level(os.getenv('LOG_LEVEL')) or logging.INFO
    logging.basicConfig(format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s', level=log_level)

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.jpg'))

    state = State(args.save, args.video)

    if args.offset:
        window = MainWindow(state, args.offset)
    else:
        window = MainWindow(state)

    move_window(window, 10, 10)
    window.show()

    app.exec()



