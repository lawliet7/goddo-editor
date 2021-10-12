import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QRect, Qt, QEvent
from PyQt5.QtGui import QPainter, QColor, QOpenGLWindow
from PyQt5.QtWidgets import QApplication

from goddo_player.ui.preview import VideoPreview


class AppWindow(QOpenGLWindow):
    def __init__(self):
        super().__init__()

        self.preview = VideoPreview(self.update, lambda: QRect(0, 0, 640, 360))

    def paintGL(self):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.geometry(), QColor("black"))

        painter.setPen(QColor("white"))
        print(f"preview  {self.preview.get_rect()}")
        painter.drawRect(self.preview.get_rect())
        self.preview.paint(painter)

        painter.end()

    def resizeGL(self, w: int, h: int) -> None:
        super().resizeGL(w, h)
        self.update()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        else:
            super().keyPressEvent(event)

    def event(self, event: QEvent) -> bool:
        self.preview.event(event)

        return super().event(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AppWindow()
    ex.show()
    ex.showMaximized()
    sys.exit(app.exec_())
