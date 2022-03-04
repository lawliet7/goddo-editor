from PyQt5.QtWidgets import QWidget


class BlankFullScreenWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.showMaximized()
        self.close()

    def reset(self):
        self.showMaximized()
        self.close()


