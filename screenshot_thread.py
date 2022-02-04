import logging

import cv2
import imutils
from PyQt5.QtCore import QRunnable, QUrl, pyqtSlot
from PyQt5.QtWidgets import QListWidgetItem

from goddo_player.utils.draw_utils import numpy_to_pixmap


class ScreenshotThread(QRunnable):
    def __init__(self, url: QUrl, signal, item: QListWidgetItem):
        super().__init__()
        self.url = url
        self.signal = signal
        self.item = item

    @pyqtSlot()
    def run(self):
        logging.info("started thread to get screenshot")

        cap = cv2.VideoCapture(self.url.path())
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 2))
        _, frame = cap.read()
        frame = imutils.resize(frame, height=108)
        pixmap = numpy_to_pixmap(frame)

        logging.info(f'emitting pixmap back to file list')
        self.signal.emit(pixmap, self.item)