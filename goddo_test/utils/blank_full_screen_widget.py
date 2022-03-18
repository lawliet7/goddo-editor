from PyQt5.QtWidgets import QWidget


class BlankFullScreenWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.showMaximized()
        self.hide()

    def reset_widget(self):
        self.showMaximized()
        self.hide()


