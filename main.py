import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import cv2


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


def get_video_dimensions(cap):
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return width, height


def get_next_frame(cap, specific_frame=None):
    if specific_frame:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 20000)

    if cap.grab():
        flag, frame = cap.retrieve()
        if flag:
            return frame


def convert_cvimg_to_qimg(cvimg):
    height, width, channel = cvimg.shape
    bytesPerLine = 3 * width
    return QImage(cvimg.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.cap = cv2.VideoCapture(r'C:\Users\William\Downloads\xvsr049.HD.wmv')
        width, height = get_video_dimensions(self.cap)

        self.label = QtWidgets.QLabel()
        # canvas = QtGui.QPixmap(800, 600)
        # self.label.setPixmap(canvas)
        frame = get_next_frame(self.cap, specific_frame=20000)
        self.label.setPixmap(QtGui.QPixmap(convert_cvimg_to_qimg(frame)))
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
    window = MainWindow()
    window.show()
    app.exec()
