import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QRect
import cv2
import imutils

from PyQt5.QtGui import QImage, QColor, QBrush


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


class Communicate(QObject):
    update_frame = pyqtSignal()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, video, initial_offset=None):
        super().__init__()

        self.move(10, 10)

        self.cap = cv2.VideoCapture(video)
        print_all_populated_openv_attrs(self.cap)
        width, height = get_video_dimensions(self.cap)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.label = QtWidgets.QLabel()
        # canvas = QtGui.QPixmap(800, 600)
        # self.label.setPixmap(canvas)
        frame = get_next_frame(self.cap, specific_frame=initial_offset)
        # scaled_frame = resize(frame, (800, 600))
        scaled_frame = imutils.resize(frame, width=1280)
        self.label.setPixmap(QtGui.QPixmap(convert_cvimg_to_qimg(scaled_frame)))
        self.setCentralWidget(self.label)

        self.current_time = get_perf_counter_as_millis()
        self.slider_circle_radius = 5
        self.slider_rect = self.get_slider_rect()

        self.c = Communicate()
        self.c.update_frame.connect(self.update_frame)

        self.timer = QTimer(self)
        self.timer.setInterval(num_frames_to_num_millis(self.fps))
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.emit_update_frame_signal)
        self.timer.start()

    def get_slider_rect(self):
        rect = self.label.geometry()
        y_of_timeline = convert_to_int(rect.height() * 0.9 + rect.top())
        return QRect(rect.left(), y_of_timeline - self.slider_circle_radius, rect.width(),
                     y_of_timeline - self.slider_circle_radius)

    def resizeEvent(self, event):
        self.slider_rect = self.get_slider_rect()
        QtWidgets.QMainWindow.resizeEvent(self, event)

    def update_frame(self):
        if not is_video_done(self.cap):
            new_time = get_perf_counter_as_millis()
            time_diff = new_time - self.current_time
            frame_diff = convert_to_int(time_diff/self.fps)

            frame = skip_until_frame(self.cap, frame_diff)
            if frame is None:
                raise Exception("File is corrupted")
            scaled_frame = imutils.resize(frame, width=1280)
            self.label.setPixmap(QtGui.QPixmap(convert_cvimg_to_qimg(scaled_frame)))
            self.current_time = new_time

            if self.label.underMouse():
                self.draw_seek_bar()

    def draw_seek_bar(self):
        painter = QtGui.QPainter(self.label.pixmap())
        painter.setPen(create_pen(color=QColor(242, 242, 242, 100)))
        rect = self.label.geometry()

        y_of_timeline = rect.height()*0.9 + rect.top()
        painter.drawLine(rect.left(),  convert_to_int(y_of_timeline), rect.right(),  convert_to_int(y_of_timeline))

        pct_done = self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        painter.setPen(create_pen(width=3, color=QColor(153, 0, 153)))
        painter.drawLine(rect.left(), convert_to_int(y_of_timeline), convert_to_int(pct_done*rect.width()+rect.left()),
                         convert_to_int(y_of_timeline))

        painter.setBrush(QBrush(QColor(153, 0, 153), Qt.SolidPattern))
        painter.drawEllipse(convert_to_int(pct_done*rect.width()+rect.left())-self.slider_circle_radius,
                            convert_to_int(y_of_timeline)-self.slider_circle_radius,
                            self.slider_circle_radius*2, self.slider_circle_radius*2)

        painter.end()

    def emit_update_frame_signal(self):
        self.c.update_frame.emit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) == 2:
        window = MainWindow(sys.argv[1])
    elif len(sys.argv) == 3:
        window = MainWindow(sys.argv[1], int(sys.argv[2]))
    else:
        raise Exception("usage: main.py {video_file} {initial offset (optional)}")
    window.show()
    app.exec()
