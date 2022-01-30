from PyQt5.QtWidgets import QLabel, QFrame


class TagWidget(QLabel):
    def __init__(self, text, delete_cb=None):
        super().__init__()

        # tag_widget_height = 25

        self.setText(text)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        # self.setMidLineWidth(10)
        # self.setLineWidth(10)

