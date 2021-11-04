import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout

from goddo_player.volume import VolumeControl


class TimelineWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(10, 60, 1024, 768)

        # p = self.palette()
        # p.setColor(self.backgroundRole(), QColor(51, 51, 51))
        # self.setPalette(p)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        # 102, 102, 102

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(QColor(51, 51, 51)))
        painter.setBrush(QBrush(painter.pen().color(), Qt.SolidPattern))
        painter.drawRect(QRect(0, 0, self.geometry().width(), 100))

        painter.setPen(QPen(QColor(64, 64, 64)))
        painter.setBrush(QBrush(painter.pen().color(), Qt.SolidPattern))
        painter.drawRect(QRect(0, 101, self.geometry().width(), self.geometry().height() - 101))

        painter.end()

        super().paintEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TimelineWindow()
    w.setWindowTitle('Simple')
    w.show()
    sys.exit(app.exec_())



