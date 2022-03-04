from PyQt5.QtWidgets import QWidget


class BlankFullScreenWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.showMaximized()

    def reset(self):
        self._max_widget.showMaximized()
        self._max_widget.hide()


