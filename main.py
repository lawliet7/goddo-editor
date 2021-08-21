import os
import sys
import time
import logging

import cv2
import imutils
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QRect, QPoint, QRunnable, pyqtSlot
from PyQt5.QtGui import QImage, QColor, QBrush, QPainter, QMouseEvent
from PyQt5.QtWidgets import QMainWindow


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


def convert_to_int(value, round_num=True):
    if round_num:
        return int(round(value))
    else:
        return int(value)


def to_frames(cap):
    fps = cap.get(cv2.CAP_PROP_FPS)
    cur_frames = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    frames = int(cur_frames % fps)
    secs = int(cur_frames / fps % 60)
    mins = int(cur_frames / fps / 60 % 60)
    hours = int(cur_frames / fps / 60 / 60 % 60)
    return hours, mins, secs, frames


def build_time_str(hours=0, mins=0, secs=0, frames=0):
    return "{}:{:02d}:{:02d}.{:02d}".format(hours, mins, secs, frames)


class MainLoopUpdateSignals(QObject):
    update_frame = pyqtSignal(int)


class AdhocUpdateSignals(QObject):
    update_frame = pyqtSignal(int)


class MainWindow(QMainWindow):
    def __init__(self, video, initial_offset=None):
        super().__init__()

        self.move(10, 10)

        app.setWindowIcon(QtGui.QIcon('icon.jpg'))

        self.cap = cv2.VideoCapture(video)
        print_all_populated_openv_attrs(self.cap)
        # width, height = get_video_dimensions(self.cap)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps_as_ms = num_frames_to_num_millis(self.fps)

        self.label = QtWidgets.QLabel()
        # canvas = QtGui.QPixmap(800, 600)
        # self.label.setPixmap(canvas)
        # frame = get_next_frame(self.cap, specific_frame=initial_offset)
        # # scaled_frame = resize(frame, (800, 600))
        # scaled_frame = imutils.resize(frame, width=1280)
        # self.label.setPixmap(QtGui.QPixmap(convert_cvimg_to_qimg(scaled_frame)))
        self.setCentralWidget(self.label)

        self.current_time = get_perf_counter_as_millis()
        self.slider_circle_radius = 5
        self.slider_rect = self.get_slider_rect()

        self.main_signals = MainLoopUpdateSignals()
        self.main_signals.update_frame.connect(self.update_frame)

        self.adhoc_signals = AdhocUpdateSignals()
        self.adhoc_signals.update_frame.connect(self.update_frame)

        self.timer = QTimer(self)
        self.timer.setInterval(self.fps_as_ms)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.emit_update_frame_signal)
        self.timer.start()

        if initial_offset:
            self.emit_update_frame_signal(initial_offset)

    def paint(self, func):
        painter = QPainter(self.label.pixmap())
        func(painter)
        painter.end()

    def get_slider_rect(self):
        rect = self.label.geometry()
        y_of_timeline = convert_to_int(rect.height() * 0.9 + rect.top())
        return QRect(rect.left(), y_of_timeline - self.slider_circle_radius-5, rect.width(),
                     self.slider_circle_radius*2+10)

    def resizeEvent(self, event):
        self.slider_rect = self.get_slider_rect()
        QtWidgets.QMainWindow.resizeEvent(self, event)

    def update_frame(self, frame_no=-1):
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
                # frame_diff = 1
                if frame_diff > 0:
                    target_frame = skip_until_frame(self.cap, frame_diff)
            elif frame_no > cur_frame and frame_no - cur_frame < 10:
                frame_diff = frame_no > cur_frame
                if frame_diff > 0:
                    target_frame = skip_until_frame(self.cap, frame_diff)
            else:
                target_frame = get_next_frame(self.cap, frame_no)
            # target_frame = get_next_frame(self.cap)

            if target_frame is not None:
                scaled_frame = imutils.resize(target_frame, width=1280)
                self.label.setPixmap(QtGui.QPixmap(convert_cvimg_to_qimg(scaled_frame)))
                self.current_time = new_time

                if self.label.underMouse():
                    self.draw_seek_bar()
            else:
                logging.debug("skipped advancing frame")

        self.main_signals.blockSignals(False)

    def draw_seek_bar(self):
        def draw_func(painter):
            painter.setPen(create_pen(color=QColor(242, 242, 242, 100)))
            rect = self.label.geometry()

            y_of_timeline = rect.height()*0.9 + rect.top()
            painter.drawLine(rect.left(),  convert_to_int(y_of_timeline), rect.right(),  convert_to_int(y_of_timeline))

            pct_done = self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            painter.setPen(create_pen(width=3, color=QColor(153, 0, 153)))
            painter.drawLine(rect.left(), convert_to_int(y_of_timeline),
                             convert_to_int(pct_done*rect.width()+rect.left()), convert_to_int(y_of_timeline))

            painter.setBrush(QBrush(QColor(153, 0, 153), Qt.SolidPattern))
            painter.drawEllipse(convert_to_int(pct_done*rect.width()+rect.left())-self.slider_circle_radius,
                                convert_to_int(y_of_timeline)-self.slider_circle_radius,
                                self.slider_circle_radius*2, self.slider_circle_radius*2)

            y_of_elapsed_time = int(y_of_timeline+self.slider_circle_radius+10)
            # self.fps
            cur_frames = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            to_frames(self.cap)
            painter.setPen(create_pen())
            painter.drawText(QPoint(5, y_of_elapsed_time), "{}:{:02d}:{:02d}.{:02d}".format(*to_frames(self.cap)))

            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frames = int(total_frames % self.fps)
            secs = int(total_frames / self.fps % 60)
            mins = int(total_frames / self.fps / 60 % 60)
            hours = int(total_frames / self.fps / 60 / 60 % 60)
            painter.setPen(create_pen())
            painter.drawText(QPoint(rect.width()-70, y_of_elapsed_time), "{}:{:02d}:{:02d}.{:02d}".format(hours, mins, secs, frames))

        self.paint(draw_func)

    def emit_update_frame_signal(self, target_frame=-1):
        self.main_signals.update_frame.emit(target_frame)

    def mousePressEvent(self, event: QMouseEvent):
        logging.debug(event.pos())
        logging.debug(self.slider_rect.contains(event.pos()))

        if self.slider_rect.contains(event.pos()):
            pct = (event.pos().x() - self.slider_rect.left()) / self.slider_rect.width()
            target_frame = convert_to_int(pct*self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            logging.debug('target frame: {}, {}'.format(pct, target_frame))

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


if __name__ == '__main__':
    log_level = convert_to_log_level(os.getenv('LOG_LEVEL')) or logging.INFO
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)

    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) == 2:
        window = MainWindow(sys.argv[1])
    elif len(sys.argv) == 3:
        window = MainWindow(sys.argv[1], int(sys.argv[2]))
    else:
        raise Exception("usage: main.py {video_file} {initial offset (optional)}")
    window.show()
    app.exec()
