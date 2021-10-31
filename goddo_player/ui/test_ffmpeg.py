import subprocess
import sys

import cv2
import imutils
import numpy as np
from PyQt5.QtCore import QEvent, Qt, QRect, QTimer
from PyQt5.QtGui import QKeyEvent, QColor, QPainter, QOpenGLWindow, QImage, QPixmap
from PyQt5.QtWidgets import QApplication

from goddo_player.ui.ffmpeg_service import FFmpegService


def read_frames(path, res):
    """Read numpy arrays of video frames. Path is the file path
       and res is the resolution as a tuple."""
    args = [
        "ffmpeg",
        "-ss",
        "12:00",
        "-i",
        path,
        "-f",
        "image2pipe",
        "-pix_fmt",
        "rgb24",
        "-vcodec",
        "rawvideo",
        "-",
    ]

    pipe = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=res[0] * res[1] * 3,
    )

    while pipe.poll() is None:
        frame = pipe.stdout.read(res[0] * res[1] * 3)
        if len(frame) > 0:
            # print('generate next one')
            array = np.frombuffer(frame, dtype="uint8")
            yield array.reshape((res[1], res[0], 3))


class TestWindow(QOpenGLWindow):
    def __init__(self, file_path):
        super().__init__()

        video_dict = FFmpegService.probe(file_path)
        print(video_dict)

        print('init')
        self.frames_gen = read_frames(file_path, (video_dict['width'], video_dict['height']))
        print('generator')

        self.setMinimumWidth(640)
        self.setMinimumHeight(360)

        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(lambda: self.update())
        self.timer.start(int(1000 / 30) + 1)

        print(self.geometry())


    def paintGL(self):
        # print('update')
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        frame = next(self.frames_gen)
        # print(f'got frame {frame.shape}')
        frame = imutils.resize(frame, height=360)
        img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

    def resizeGL(self, w: int, h: int) -> None:
        super().resizeGL(w, h)
        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    file_path = 'C:/Users/William/Google Drive/ml/giga/heels/Copy of BCA-10.wmv'
    video_dict = FFmpegService.probe(file_path)
    print(video_dict)

    cap = cv2.VideoCapture(file_path)
    print(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    app = QApplication(sys.argv)
    ex = TestWindow(file_path)
    ex.show()
    sys.exit(app.exec_())
