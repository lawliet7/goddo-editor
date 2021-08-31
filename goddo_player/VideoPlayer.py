import cv2
from PyQt5.QtCore import QObject


class VideoPlayer(QObject):
    def __init__(self, video_path):
        super().__init__()

        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_current_frame(self):
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
            if flag:
                return frame
