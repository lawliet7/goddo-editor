import sys

from PyQt5.QtCore import QRect, Qt, QEvent, QObject
from PyQt5.QtGui import QPainter, QColor, QOpenGLWindow, QKeyEvent
from PyQt5.QtWidgets import QApplication

from goddo_player.ui.preview import VideoPreview


class PreviewWindow(QOpenGLWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumWidth(640)
        self.setMinimumHeight(360)
        self.preview = VideoPreview(self.update, lambda: QRect(0, 0, self.size().width(), self.size().height()))

        self.installEventFilter(self)

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

    # cap = cv2.VideoCapture('file:///C:/Users/William/Downloads/xvsr049.HD.wmv')
    # print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # print(cap.isOpened())
