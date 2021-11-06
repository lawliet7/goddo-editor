import os
import sys

from PyQt5.QtWidgets import QApplication

from goddo_player.ui.file_list import FileList
from goddo_player.ui.preview_window import PreviewWindow
from goddo_player.ui.state_store import State
from goddo_player.ui.timeline_window import TimelineWindow


def main():
    app = QApplication(sys.argv)

    preview_window = PreviewWindow('source')
    file_list = FileList()
    timeline_window = TimelineWindow()

    State().load_slot.emit(os.path.join('..', '..', 'saves', 'a.json'))
    preview_window.show()
    file_list.show()
    timeline_window.show()

    sys.exit(app.exec_())

    # x = '123|'
    # y = x.split('|')
    # print(y)
    #
    # import re
    # z = re.fullmatch('^[0-9]*\\|[0-9]*$', x)
    # print(z)



if __name__ == '__main__':
    main()
