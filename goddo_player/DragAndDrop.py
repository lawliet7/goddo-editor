from dataclasses import dataclass


@dataclass
class VideoClipDragItem:
    in_frame: int
    out_frame: int
    video_name: str
    fps: float

    @property
    def total_frames(self):
        return self.out_frame - self.in_frame

    @property
    def total_secs(self):
        return self.total_frames / self.fps
