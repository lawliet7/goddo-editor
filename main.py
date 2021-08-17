import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import cv2
import imutils


# class _Bar(QtWidgets.QWidget):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.setSizePolicy(
#             QtWidgets.QSizePolicy.MinimumExpanding,
#             QtWidgets.QSizePolicy.MinimumExpanding
#         )
#
#
#
#     def sizeHint(self):
#         return QtCore.QSize(40, 120)
#
#     def paintEvent(self, e):
#         painter = QtGui.QPainter(self)
#
#         brush = QtGui.QBrush()
#         brush.setColor(QtGui.QColor('black'))
#         brush.setStyle(Qt.SolidPattern)
#         rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
#         painter.fillRect(rect, brush)
#
#         # Get current state.
#         dial = self.parent()._dial
#         vmin, vmax = dial.minimum(), dial.maximum()
#         value = dial.value()
#
#         pen = painter.pen()
#         pen.setColor(QtGui.QColor('red'))
#         painter.setPen(pen)
#
#         font = painter.font()
#         font.setFamily('Times')
#         font.setPointSize(18)
#         painter.setFont(font)
#
#         painter.drawText(25, 25, "{}-->{}<--{}".format(vmin, value, vmax))
#         painter.end()
#
#     def _trigger_refresh(self):
#         self.update()
#
# class PowerBar(QtWidgets.QWidget):
#     """
#     Custom Qt Widget to show a power bar and dial.
#     Demonstrating compound and custom-drawn widget.
#     """
#
#     def __init__(self, steps=5, *args, **kwargs):
#         super(PowerBar, self).__init__(*args, **kwargs)
#
#         layout = QtWidgets.QVBoxLayout()
#         self._bar = _Bar()
#         layout.addWidget(self._bar)
#
#         self._dial = QtWidgets.QDial()
#         layout.addWidget(self._dial)
#
#         self.setLayout(layout)
#
#         self._dial.valueChanged.connect(self._bar._trigger_refresh)
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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, video):
        super().__init__()

        self.cap = cv2.VideoCapture(video)
        print(print_all_populated_openv_attrs(self.cap))
        width, height = get_video_dimensions(self.cap)

        self.label = QtWidgets.QLabel()
        # canvas = QtGui.QPixmap(800, 600)
        # self.label.setPixmap(canvas)
        frame = get_next_frame(self.cap, specific_frame=20000)
        # scaled_frame = resize(frame, (800, 600))
        scaled_frame = imutils.resize(frame, width=1024)
        self.label.setPixmap(QtGui.QPixmap(convert_cvimg_to_qimg(scaled_frame)))
        self.setCentralWidget(self.label)
        self.draw_something()

    def draw_something(self):
        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor('white'))
        painter.setPen(pen)
        painter.drawLine(10, 10, 300, 200)
        painter.end()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(sys.argv[1])
    window.show()
    app.exec()
