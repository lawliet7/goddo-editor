import sys

import cv2
from PyQt5.QtCore import QRect, Qt, QEvent, QObject
from PyQt5.QtGui import QPainter, QColor, QOpenGLWindow, QKeyEvent, QFont
from PyQt5.QtWidgets import QApplication

from goddo_player.ui.preview import VideoPreview


class PreviewWindow(QOpenGLWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumWidth(640)
        self.setMinimumHeight(360)
        self.preview = VideoPreview(self, lambda: QRect(0, 0, self.size().width(), self.size().height()))

        self.installEventFilter(self)

    def initializeGL(self) -> None:
        super().initializeGL()

        # just to load the text engine or something, first time writing text always take time
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawText(0, 0, ' ')
        painter.end()

    def paintGL(self):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(QRect(0, 0, self.size().width(), self.size().height()), QColor("black"))

        painter.setPen(QColor("white"))
        self.preview.paint(painter)

        painter.end()

    def resizeGL(self, w: int, h: int) -> None:
        super().resizeGL(w, h)
        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        else:
            super().keyPressEvent(event)

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        if super().eventFilter(obj, event):
            return True

        return self.preview.eventFilter(obj, event)

    def event(self, event: QEvent) -> bool:
        # print(event.type())
        if event.type() != QEvent.ChildAdded:
            self.preview.event(event)

        return super().event(event)


def main():
    app = QApplication(sys.argv)
    ex = PreviewWindow()
    ex.show()
    # ex.showMaximized()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

