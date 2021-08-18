import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
import cv2
import imutils

from PyQt5.QtGui import QImage


def print_all_populated_openv_attrs(cap):
    for attr in [x for x in dir(cv2) if x.startswith('CAP_PROP_')]:
      attr_value = cap.get(getattr(cv2,attr))
      if attr_value != 0:
        print('{} = {}'.format(attr, attr_value))


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
    for i in range(num_frames):
        frame = get_next_frame(cap)
    return frame


class Communicate(QObject):
    update_frame = pyqtSignal()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, video):
        super().__init__()

        self.cap = cv2.VideoCapture(video)
        print(print_all_populated_openv_attrs(self.cap))
        width, height = get_video_dimensions(self.cap)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.label = QtWidgets.QLabel()
        # canvas = QtGui.QPixmap(800, 600)
        # self.label.setPixmap(canvas)
        frame = get_next_frame(self.cap, specific_frame=10000)
        # scaled_frame = resize(frame, (800, 600))
        scaled_frame = imutils.resize(frame, width=1024)
        self.label.setPixmap(QtGui.QPixmap(convert_cvimg_to_qimg(scaled_frame)))
        self.setCentralWidget(self.label)
        self.draw_something()

        self.current_time = int(time.perf_counter() * 1000)
        print(self.current_time)
        # print(time.perf_counter())

        self.c = Communicate()
        self.c.update_frame.connect(self.update_frame)

        self.timer = QTimer(self)
        self.timer.setInterval(num_frames_to_num_millis(self.fps))
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.emit_update_frame_signal)
        self.timer.start()

    def draw_something(self):
        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor('white'))
        painter.setPen(pen)
        painter.drawLine(10, 10, 300, 200)
        painter.end()

    def update_frame(self):
        # print("updating frame")
        # print(time.perf_counter())
        new_time = get_perf_counter_as_millis()
        time_diff = new_time - self.current_time
        frame_diff = int(round(time_diff/self.fps))
        frame = skip_until_frame(self.cap, frame_diff)
        scaled_frame = imutils.resize(frame, width=1024)
        self.label.setPixmap(QtGui.QPixmap(convert_cvimg_to_qimg(scaled_frame)))
        self.current_time = new_time
        # self.update()

    def emit_update_frame_signal(self):
        self.c.update_frame.emit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(sys.argv[1])
    window.show()
    app.exec()
