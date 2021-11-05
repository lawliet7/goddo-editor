import os

import cv2
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot, Qt

from goddo_player.ui.state_store import State


class VideoPlayer(QObject):
    next_frame_slot = pyqtSignal(object, int)

    def __init__(self):
        super().__init__()

        self.state = State()
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

        self.state.play_slot.connect(self.play_handler)
        self.state.pause_slot.connect(self.pause_handler)
        self.state.jump_frame_slot.connect(self.__jump_frame_handler)

    def __jump_frame_handler(self, name, frame_no):
        frame = self.get_next_frame(specific_frame=frame_no)
        self.cur_frame = frame
        self.cur_frame_no = frame_no
        self.next_frame_slot.emit(frame, frame_no)

    @property
    def is_playing(self):
        return self.timer.isActive()

    @pyqtSlot()
    def play_handler(self):
        if not self.timer.isActive():
            self.__start_timer()

    @pyqtSlot()
    def pause_handler(self):
        print('pause')
        if self.timer.isActive():
            print('stopping timer')
            self.timer.stop()
            self.state.post_pause_slot.emit('source', self.cur_frame_no)

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
            self.timer.deleteLater()
            self.timer = QTimer()
            self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.__emit_next_frame)
        self.__start_timer()

        print(f'source switched to {file_path} fps {self.fps}')

    def __start_timer(self):
        self.timer.start(int(1000 / self.fps)+1)

    def __emit_next_frame(self):
        self.cur_frame = self.get_next_frame()
        self.cur_frame_no = self.cap.get(cv2.CAP_PROP_POS_FRAMES)

        self.next_frame_slot.emit(self.cur_frame, self.cur_frame_no)

