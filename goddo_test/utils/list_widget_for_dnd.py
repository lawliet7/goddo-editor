from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QWidget, QListWidget, QLabel, QListWidgetItem

from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.window_util import local_to_global_pos


class ListWidgetForDnd:
    def __init__(self):
        super().__init__()

        self.list_widget = QListWidget()
        self.list_widget.itemPressed.connect(self._on_item_clicked)

    def show(self):
        self.list_widget.show()

    def hide(self):
        self.list_widget.hide()

    def add_item(self, txt):
        item = QListWidgetItem()
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, QLabel(txt))

    def get_item_and_widget(self, idx):
        item = self.list_widget.item(idx)
        item_widget = self.list_widget.itemWidget(item)
        return item, item_widget

    def get_count(self):
        return self.list_widget.count()

    def item_widget_pos(self, idx, global_pos=True):
        _, item_widget = self.get_item_and_widget(idx)

        if global_pos:
            return local_to_global_pos(item_widget)
        else:
            return item_widget.pos()

    def _on_item_clicked(self, item):
        path = self.list_widget.itemWidget(item).text()

        drag = QDrag(self.list_widget)
        mime_data = QMimeData()
        mime_data.setUrls([file_to_url(path)])
        drag.setMimeData(mime_data)
        drag.exec()

    def reset_widget(self):
        self.list_widget.clear()
        self.list_widget.hide()
