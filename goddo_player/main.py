import logging
import os
import sys
import threading
import time

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QRect, QPoint, QEvent
from PyQt5.QtGui import QImage, QColor, QBrush, QPainter, QMouseEvent, QWindow, QOpenGLWindow, QSurfaceFormat, QPen
from PyQt5.QtWidgets import QWidget, QApplication, QStyle

from goddo_player.AudioPlayer import AudioPlayer
from number_utils import convert_to_int


def print_all_populated_openv_attrs(cap):
    for attr in [x for x in dir(cv2) if x.startswith('CAP_PROP_')]:
        attr_value = cap.get(getattr(cv2, attr))
        if attr_value != 0:
            logging.info('{} = {}'.format(attr, attr_value))


def get_video_dimensions(cap):
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return width, height


def get_next_frame(cap, specific_frame=None):
    if specific_frame:
        cap.set(cv2.CAP_PROP_POS_FRAMES, specific_frame)

    if cap.grab():
        flag, frame = cap.retrieve()
        if flag:
            return frame


def convert_cvimg_to_qimg(cvimg):
    height, width, channel = cvimg.shape
    bytes_per_line = 3 * width
    return QImage(cvimg.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()


def scale_image(img, scale):
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    dim = (width, height)
    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)


def num_frames_to_num_millis(num_frames):
    return int(round(1000 / num_frames))


def get_perf_counter_as_millis():
    return int(time.perf_counter() * 1000)


def skip_until_frame(cap, num_frames):
    frame = None
    for i in range(num_frames):
        if is_video_done(cap):
            break
        frame = get_next_frame(cap)
    return frame


def create_pen(width=1, color=Qt.white):
    pen = QtGui.QPen()
    pen.setWidth(width)
    pen.setColor(color)
    return pen


def is_video_done(cap):
    return cap.get(cv2.CAP_PROP_POS_FRAMES) >= cap.get(cv2.CAP_PROP_FRAME_COUNT)


def frames_to_time_components(total_frames, fps):
    frames = int(total_frames % fps)
    secs = int(total_frames / fps % 60)
    mins = int(total_frames / fps / 60 % 60)
    hours = int(total_frames / fps / 60 / 60 % 60)
    return hours, mins, secs, frames


def build_time_str(hours=0, mins=0, secs=0, frames=0):
    return "{}:{:02d}:{:02d}.{:02d}".format(hours, mins, secs, frames)


class MainLoopUpdateSignals(QObject):
    update_frame = pyqtSignal(int)


class AdhocUpdateSignals(QObject):
    update_frame = pyqtSignal(int)


class MainWindow(QOpenGLWindow):
    def __init__(self, video, initial_offset=None):
        super().__init__()

        self.cap = cv2.VideoCapture(video)
        print_all_populated_openv_attrs(self.cap)
        # width, height = get_video_dimensions(self.cap)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps_as_ms = num_frames_to_num_millis(self.fps)
        self.pixmap = None

        self.audio_player = AudioPlayer(video, self.fps)

        # self.label = QtWidgets.QLabel()
        # self.setCentralWidget(self.label)

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

        # if initial_offset:
        #     self.emit_update_frame_signal(initial_offset)

        # self.worker = Worker(video_path=video)
        # self.cur_audio_pos = 0
        # self.threadpool = QThreadPool()
        # self.threadpool.start(self.worker)

        # self.player = Player()
        # self.source = load(video)
        # self.source.video_format = None
        # self.video_path = video
        # self.player.queue(self.source)
        # self.cur_audio_pos = 0
        # self.player.play()
        # self.player.volume = 0.1

        self.is_mouse_over = False


    def initializeGL(self) -> None:
        super().initializeGL()

        fmt = QSurfaceFormat()
        fmt.setSamples(4)
        QSurfaceFormat.setDefaultFormat(fmt)

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        new_dim = get_resize_dim_keep_aspect(width, height, 1280)
        self.resize(*new_dim)

        # get slider rect
        distince_from_rect_to_bottom = 100
        height_of_slider_rect = 30
        self.slider_rect = QRect(0,new_dim[1]-distince_from_rect_to_bottom, new_dim[0], height_of_slider_rect)

        # draw text seems to need to be 'warmed up' to run quickly
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawText(QPoint(0, 0), "x")
        painter.end()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QMouseEvent.Enter:
            return True
        elif event.type() == QMouseEvent.Leave:
            return True
        return super().eventFilter(obj, event)

    def event(self, event: QtCore.QEvent) -> bool:
        if event.type() == QMouseEvent.Enter:
            logging.debug('mouse enter')
            self.is_mouse_over = True
            return True
        elif event.type() == QMouseEvent.Leave:
            logging.debug('mouse leave')
            self.is_mouse_over = False
            return True
        return super().event(event)

    def paintGL(self) -> None:
        # super().paintGL()

        if self.pixmap is not None:
            logging.debug("painting")
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawPixmap(0, 0, self.pixmap)
            painter.end()

    def paintOverGL(self) -> None:
        # super().paintOverGL()

        logging.debug(self.is_mouse_over)
        if self.is_mouse_over:
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHint(QPainter.Antialiasing)
            self.draw_seek_bar(painter)

            # print(self.slider_rect)
            # painter.setPen(create_pen(color=QColor(242, 242, 242, 100)))
            # painter.drawRect(self.slider_rect)

            painter.end()

    # def get_slider_rect(self):
    #     rect = self.geometry()
    #     y_of_timeline = convert_to_int(rect.height() * 0.8 + rect.top())
    #     return QRect(rect.left(), y_of_timeline - self.slider_circle_radius-5, rect.width(),
    #                  self.slider_circle_radius*2+10)

    def update_frame(self, frame_no=-1):
        logging.debug("[{}] updating frame".format(threading.get_ident()))
        self.main_signals.blockSignals(True)
        # print('updating frame {}'.format(frame_no))
        if not is_video_done(self.cap) or (is_video_done(self.cap) and frame_no > -1):
            new_time = get_perf_counter_as_millis()
            cur_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            target_frame = None
            if frame_no < 0:
                logging.debug("in frame < 0, {} - {} = {}".format(new_time, self.current_time,
                                                                  new_time - self.current_time))
                time_diff = new_time - self.current_time
                frame_diff = convert_to_int(time_diff/self.fps_as_ms)
                logging.debug('diffs {} {}'.format(time_diff, frame_diff))
                frame_diff = 1
                if frame_diff > 0:
                    target_frame = skip_until_frame(self.cap, frame_diff)
                self.audio_player.emit_play_audio_signal(frame_diff)
            elif frame_no > cur_frame and frame_no - cur_frame < 10:
                frame_diff = frame_no > cur_frame
                if frame_diff > 0:
                    target_frame = skip_until_frame(self.cap, frame_diff)
                    self.audio_player.emit_play_audio_signal(frame_diff)
            else:
                target_frame = get_next_frame(self.cap, frame_no)
                self.audio_player.emit_go_to_audio_signal(frame_no)
            # target_frame = get_next_frame(self.cap)

            if target_frame is not None:
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                new_dim = get_resize_dim_keep_aspect(width, height, 1280)
                scaled_frame = cv2.resize(target_frame, new_dim, interpolation=cv2.INTER_AREA)
                self.pixmap = QtGui.QPixmap(convert_cvimg_to_qimg(scaled_frame))
                self.update()
                self.current_time = new_time
                logging.info("update audio pos")
            else:
                logging.debug("skipped advancing frame")

        self.main_signals.blockSignals(False)

    def draw_seek_bar(self, painter: QPainter):
        painter.setPen(create_pen(color=QColor(242, 242, 242, 100)))

        y_of_timeline = self.slider_rect.height() / 2 + self.slider_rect.top()
        painter.drawLine(self.slider_rect.left(),  convert_to_int(y_of_timeline), self.slider_rect.right(),  convert_to_int(y_of_timeline))

        pct_done = self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        painter.setPen(create_pen(width=3, color=QColor(153, 0, 153)))
        painter.drawLine(self.slider_rect.left(), convert_to_int(y_of_timeline),
                         convert_to_int(pct_done*self.slider_rect.width()+self.slider_rect.left()), convert_to_int(y_of_timeline))

        painter.setBrush(QBrush(QColor(153, 0, 153), Qt.SolidPattern))
        painter.drawEllipse(convert_to_int(pct_done*self.slider_rect.width()+self.slider_rect.left())-self.slider_circle_radius,
                            convert_to_int(y_of_timeline)-self.slider_circle_radius,
                            self.slider_circle_radius*2, self.slider_circle_radius*2)

        y_of_elapsed_time = int(y_of_timeline+self.slider_circle_radius+10)
        painter.setPen(create_pen())

        cur_frames = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        painter.drawText(QPoint(5, y_of_elapsed_time),
                         "{}:{:02d}:{:02d}.{:02d}".format(*frames_to_time_components(cur_frames, self.fps)))

        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        painter.drawText(QPoint(self.slider_rect.width()-70, y_of_elapsed_time),
                         "{}:{:02d}:{:02d}.{:02d}".format(*frames_to_time_components(total_frames, self.fps)))

        painter.setPen(QPen())
        painter.setBrush(QBrush(QColor(153, 0, 153), Qt.NoBrush))

    def emit_update_frame_signal(self, target_frame=-1):
        self.main_signals.update_frame.emit(target_frame)

    def mousePressEvent(self, event: QMouseEvent):
        logging.debug(event.pos())
        logging.debug(self.slider_rect.contains(event.pos()))

        if self.slider_rect.contains(event.pos()):
            pct = (event.pos().x() - self.slider_rect.left()) / self.slider_rect.width()
            target_frame = convert_to_int(pct*self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            logging.info('target frame: {}, {}'.format(pct, target_frame))

            self.main_signals.blockSignals(True)
            self.adhoc_signals.update_frame.emit(target_frame)
            self.main_signals.blockSignals(False)

    def mouseReleaseEvent(self, event):
        cursor = QtGui.QCursor()
        logging.debug(cursor.pos())


def convert_to_log_level(log_level_str: str):
    if log_level_str:
        return logging.getLevelName(log_level_str.upper())
    else:
        return None


def move_window(window_instance, x, y):
    if isinstance(window_instance, QWidget):
        window_instance.move(x, y)
    elif isinstance(window_instance, QWindow):
        # opengl windows don't take into account title bar
        title_bar_height = QApplication.style().pixelMetric(QStyle.PM_TitleBarHeight)
        window_instance.setX(x)
        window_instance.setY(y+title_bar_height)
    else:
        raise Exception("Invalid window type")


def get_resize_dim_keep_aspect(original_width: int, original_height: int, target_width: int):
    if original_width > target_width:
        new_width = target_width
        adjusted_height = convert_to_int(new_width * original_height / original_width)
    else:
        new_width = int(original_width)
        adjusted_height = int(original_height)

    return new_width, adjusted_height


if __name__ == '__main__':
    log_level = convert_to_log_level(os.getenv('LOG_LEVEL')) or logging.INFO
    logging.basicConfig(format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s', level=log_level)

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.jpg'))

    if len(sys.argv) == 2:
        window = MainWindow(sys.argv[1])
    elif len(sys.argv) == 3:
        window = MainWindow(sys.argv[1], int(sys.argv[2]))
    else:
        raise Exception("usage: main.py {video_file} {initial offset (optional)}")

    move_window(window, 10, 10)
    window.show()
    app.exec()
