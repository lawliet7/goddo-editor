import os
import sys

from PyQt5.QtWidgets import QApplication

from goddo_player.ui.file_list import FileList
from goddo_player.ui.preview_window import PreviewWindow
from goddo_player.ui.state_store import State


def main():
    app = QApplication(sys.argv)

    preview_window = PreviewWindow('source')
    file_list = FileList()

    State().load_slot.emit(os.path.join('..', '..', 'saves', 'a.json'))
    preview_window.show()
    file_list.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
