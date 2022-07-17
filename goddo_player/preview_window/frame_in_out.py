from dataclasses import dataclass, field


@dataclass(frozen=True)
class FrameInOut:
    in_frame: int = field(default=None)
    out_frame: int = field(default=None)

    def __post_init__(self):
        if self.in_frame is not None and type(self.in_frame) != int:
            raise Exception(f'in_frame needs to be an int but instead it is a {type(self.in_frame)}')

        if self.out_frame is not None and type(self.out_frame) != int:
            raise Exception(f'out_frame needs to be an int but instead it is a {type(self.out_frame)}')

        if self.in_frame and self.out_frame and self.in_frame > self.out_frame:
            raise Exception(f'in frame({self.in_frame} > out frame({self.out_frame})')

    def update_in_frame(self, in_frame: int):
        out_frame = None if self.out_frame and in_frame and self.out_frame < in_frame else self.out_frame
        return FrameInOut(in_frame, out_frame)

    def update_out_frame(self, out_frame: int):
        in_frame = None if self.in_frame and out_frame and self.in_frame > out_frame else self.in_frame
        return FrameInOut(in_frame, out_frame)

    def get_no_of_frames(self, total_frames):
        # frame start from 1
        if self.out_frame and self.in_frame:
            return self.out_frame - self.in_frame + 1
        elif self.in_frame:
            return total_frames - self.in_frame + 1
        elif self.out_frame:
            return self.out_frame
        else:
            return 0

    def get_resolved_in_frame(self):
        return self.in_frame if self.in_frame is not None else 1

    def get_resolved_out_frame(self, total_frames):
        return self.out_frame if self.out_frame is not None else total_frames

    def contains_frame(self, frame_no, total_frames):
        if self.get_resolved_in_frame() <= frame_no <= self.get_resolved_out_frame(total_frames):
            return True
        else:
            return False
