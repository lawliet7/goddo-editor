import os
import sys

import cv2
import imutils
from PyQt5.QtWidgets import QApplication

from goddo_player.ui.file_list import FileList
from goddo_player.ui.preview_window import PreviewWindow
from goddo_player.ui.state_store import State


def main():
    app = QApplication(sys.argv)

    State().load_save(os.path.join('..', '..', 'state', 'a.json'))

    ex = PreviewWindow('source')
    ex.show()
    file_list = FileList()
    file_list.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

    # print('C:/Users/William/Downloads/9convert.com - Girls Generation  Genie  Music Core 20090718_1080p.mp4'.isascii())
    # print(os.path.exists('C:/Users/William/Downloads/9convert.com - Girls Generation  Genie 소  Music Core 20090718_1080p.mp4'))
    # cap = cv2.VideoCapture("/C:/Users/William/Downloads/9convert.com - Girls Generation  Genie 소  Music Core 20090718_1080p".encode('utf-8').decode('unicode-escape'))
    # # print(int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 2))
    # # cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 2))
    #
    # # if cap.grab():
    # #     flag, frame = cap.retrieve()
    # #     if flag:
    # #         print(frame)
    #
    # # cap.grab()
    # _, frame = cap.read()
    # # frame = cap.read()
    # # print(frame)
    # frame = imutils.resize(frame, height=100)
    # print(f'frame size={frame.shape}')
