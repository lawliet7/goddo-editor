import sys

from PyQt5.QtWidgets import QApplication

from goddo_player.ui.file_list import FileList
from goddo_player.ui.preview_window import PreviewWindow


def main():
    app = QApplication(sys.argv)
    ex = PreviewWindow()
    ex.show()
    file_list = FileList()
    file_list.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
