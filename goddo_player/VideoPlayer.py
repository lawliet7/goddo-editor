import os

import cv2
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot, Qt

from goddo_player.ui.state_store import State


class VideoPlayer(QObject):
    next_frame_slot = pyqtSignal(object, int)
    play_slot = pyqtSignal()
    pause_slot = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.state = State(os.path.join('..', '..', 'state', 'a.json'))
        self.position = -1
        self.cap = None
        self.fps = -1
        self.total_frames = 0
        self.cur_frame = None
        self.cur_frame_no = 0

        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)

        # if self.state.video_file:
        #     self.__init_cap(self.state.video_file)

        # self.state.update_preview_file_slot.connect(self.switch_source)

        self.play_slot.connect(self.play_handler)
        self.pause_slot.connect(self.pause_handler)

    @property
    def is_playing(self):
        return self.timer.isActive()

    @pyqtSlot()
    def play_handler(self):
        if not self.timer.isActive():
            self.timer.start(int(1000 / self.fps)+1)

    @pyqtSlot()
    def pause_handler(self):
        print('pause')
        if self.timer.isActive():
            print('stopping timer')
            self.timer.stop()

    def __init_cap(self, video_file):
        self.cap = cv2.VideoCapture(video_file)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def video_path(self):
        # return self.state.video_file
        return self.state.preview_windows[0]["video_file"]

    def get_current_frame_no(self):
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) if self.cap else -1

    def is_video_done(self):
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES) >= self.cap.get(cv2.CAP_PROP_FRAME_COUNT) if self.cap else True

    def skip_until_frame(self, num_frames):
        frame = None
        for i in range(num_frames):
            if self.is_video_done():
                break
            frame = self.get_next_frame()
        return frame

    def get_next_frame(self, specific_frame=None):
        if self.cap:
            if specific_frame:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, specific_frame)

            if self.cap.grab():
                flag, frame = self.cap.retrieve()
                self.position = self.get_current_frame_no()
                if flag:
                    return frame
        else:
            return None

    def get_video_dimensions(self):
        if self.cap:
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            return width, height
        else:
            return 0, 0

    def switch_source(self, x, file_path):
        print('------switching source')
        if self.cap:
            self.cap.release()

        self.__init_cap(file_path)

        if self.timer.isActive():
            self.timer.stop()
        self.timer.timeout.connect(self.__emit_next_frame)
        self.timer.start(int(1000 / self.fps)+1)

        print(f'source switched to {file_path}')

    def __emit_next_frame(self):
        self.cur_frame = self.get_next_frame()
        self.cur_frame_no = self.cap.get(cv2.CAP_PROP_POS_FRAMES)

        self.next_frame_slot.emit(self.cur_frame, self.cur_frame_no)

