import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout

from goddo_player.sliders2 import VolumeControl


class TimelineWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(10, 60, 1024, 768)

        # p = self.palette()
        # p.setColor(self.backgroundRole(), QColor(51, 51, 51))
        # self.setPalette(p)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        height_of_meter_panel = 50

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(QColor(51, 51, 51)))
        painter.setBrush(QBrush(painter.pen().color(), Qt.SolidPattern))
        painter.drawRect(QRect(0, 0, self.geometry().width(), height_of_meter_panel))

        painter.setPen(QPen(QColor(64, 64, 64)))
        painter.setBrush(QBrush(painter.pen().color(), Qt.SolidPattern))
        painter.drawRect(QRect(0, height_of_meter_panel+1, self.geometry().width(), self.geometry().height() - (height_of_meter_panel-1)))

        painter.setPen(QPen(QColor('white')))
        painter.setBrush(QBrush(painter.pen().color(), Qt.NoBrush))
        tick_spacing = 10
        x = 0
        while x < self.geometry().width():
            line_height = 30 if x % (tick_spacing*10) == 0 else 20 if x % (tick_spacing*5) == 0 else 10
            painter.drawLine(x, height_of_meter_panel, x, height_of_meter_panel-line_height)
            x += tick_spacing

        painter.end()

        super().paintEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TimelineWindow()
    w.setWindowTitle('Simple')
    w.show()
    sys.exit(app.exec_())



