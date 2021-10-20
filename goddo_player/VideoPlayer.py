import cv2
from PyQt5.QtCore import QObject


class VideoPlayer(QObject):
    def __init__(self, state):
        super().__init__()

        self.state = state
        self.__init_cap(self.state.video_file)

    def __init_cap(self, video_file):
        self.cap = cv2.VideoCapture(video_file)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def video_path(self):
        return self.state.video_file

    def get_current_frame_no(self):
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def is_video_done(self):
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES) >= self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

    def skip_until_frame(self, num_frames):
        frame = None
        for i in range(num_frames):
            if self.is_video_done():
                break
            frame = self.get_next_frame()
        return frame

    def get_next_frame(self, specific_frame=None):
        if specific_frame:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, specific_frame)

        if self.cap.grab():
            flag, frame = self.cap.retrieve()
            self.state.source['position'] = self.get_current_frame_no()
            if flag:
                return frame

    def get_video_dimensions(self):
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return width, height

    def switch_source(self, file_path):
        self.cap.release()
        self.__init_cap(file_path)
        print(f'source switched to {file_path}')

