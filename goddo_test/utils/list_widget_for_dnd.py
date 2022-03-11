from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QWidget, QListWidget, QLabel, QListWidgetItem

from goddo_player.utils.url_utils import file_to_url


class ListWidgetForDnd(QListWidget):
    def __init__(self):
        super().__init__()

        self.itemPressed.connect(self.on_item_clicked)

    def add_item_text(self, txt):
        item = QListWidgetItem()
        self.addItem(item)
        self.setItemWidget(item, QLabel(txt))

    def on_item_clicked(self, item):
        path = self.itemWidget(item).text()

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setUrls([file_to_url(path)])
        drag.setMimeData(mime_data)
        drag.exec()

    def reset_widget(self):
        self.clear()
        self.hide()
