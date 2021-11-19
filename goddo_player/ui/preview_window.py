from PyQt5.QtCore import QRect, Qt, QEvent, QObject, QMimeData
from PyQt5.QtGui import QPainter, QColor, QOpenGLWindow, QKeyEvent, QMouseEvent, QDrag
from PyQt5.QtWidgets import QApplication

from goddo_player.ui.preview import VideoPreview, FrameInOut
from goddo_player.ui.state_store import State


class PreviewWindow(QOpenGLWindow):
    def __init__(self, name):
        super().__init__()

        self.setTitle("強姦方法")
        self.setGeometry(501, 31, 640, 360)

        self.state = State()
        self.state.new_preview_slot.emit(name)

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

    def paintGL(self):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # todo: clear screen if no file loaded or aspect ratio is not same as window
        # aspect1 = self.preview.get_rect().width() / self.preview.get_rect().height()
        # aspect2 = self.preview.video_player.cur_frame.shape[1] / self.preview.video_player.cur_frame.shape[0]
        # if not self.preview.video_player.video_path or abs(aspect1 / aspect2 - 1) <= 0.1:
        #     print(f'clear {time.time()}')
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        frame_in_out: FrameInOut = self.state.preview_windows['source']['frame_in_out']
        if frame_in_out.in_frame is not None or frame_in_out.out_frame is not None:
            drag = QDrag(self)
            mime_data = QMimeData()
            frame_in_out: FrameInOut = self.state.preview_windows["source"]['frame_in_out']
            mime_data.setText(f'{frame_in_out.in_frame or ""}|{frame_in_out.out_frame or ""}')
            drag.setMimeData(mime_data)
            drag.exec()



