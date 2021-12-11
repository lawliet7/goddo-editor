from dataclasses import dataclass

from tinydb.table import Document


@dataclass
class VideoClipDragItem:
    in_frame: int
    out_frame: int
    fps: float
    video: Document

    @property
    def video_id(self):
        return self.video.doc_id

    @property
    def total_frames(self):
        return self.out_frame - self.in_frame

    @property
    def total_secs(self):
        return self.total_frames / self.fps
