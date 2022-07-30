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

    def open_dialog(self, fn):
        self._dialog.finished.connect(fn)
        self._dialog.show()



