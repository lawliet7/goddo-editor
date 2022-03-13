import logging

import cv2
import imutils
from PyQt5.QtCore import QRunnable, pyqtSlot
from PyQt5.QtWidgets import QListWidgetItem

from goddo_player.app.video_path import VideoPath
from goddo_player.utils.draw_utils import numpy_to_pixmap


class ScreenshotThread(QRunnable):
    def __init__(self, video_path: VideoPath, signal, item: QListWidgetItem):
        super().__init__()
        self.video_path = video_path
        self.signal = signal
        self.item = item

    @pyqtSlot()
    def run(self):
        logging.debug("started thread to get screenshot")

        cap = cv2.VideoCapture(self.video_path.str())
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 2))
        _, frame = cap.read()
        frame = imutils.resize(frame, height=108)
        pixmap = numpy_to_pixmap(frame)

        logging.debug(f'emitting pixmap back to file list')
        self.signal.emit(pixmap, self.item)
