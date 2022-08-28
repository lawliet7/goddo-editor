import logging
from typing import Callable
from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

class LoadingDialog(QObject):
    # open_dialog = pyqtSignal(Callable)

    class _MyDialog(QDialog):
        def __init__(self):
            super().__init__()

            self.setWindowTitle('Loading Audio...')
            self.setModal(True)
            self.resize(200, 200)

            self.label = QLabel(self)
            self.label.setGeometry(0, 0, 200, 200)

            self.movie = QMovie("goddo_player\\loader.gif")

            self.label.setMovie(self.movie)

            # self.show()

            self.movie.start()

    def __init__(self):
        super().__init__()

        self._dialog = self._MyDialog()
        self._current_callback = None
        self._dialog.finished.connect(self._callback)

    def _callback(self, result: int):
        if self._current_callback:
            self._current_callback(result)

    def isHidden(self):
        return self._dialog.isHidden()

    def open_dialog(self, fn: Callable[[int],None] = None):
        if self._dialog.isHidden():
            self._current_callback = fn
            self._dialog.show()
        else:
            logging.error('dialog is hidden')

    def close(self):
        self._dialog.close()



