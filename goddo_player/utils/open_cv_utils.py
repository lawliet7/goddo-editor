import cv2

def create_video_capture(path: str):
    return cv2.VideoCapture(path)

def get_cur_frame_no(cap):
    return int(cap.get(cv2.CAP_PROP_POS_FRAMES)) if cap else 0

def set_cap_pos(cap, frame_no: int, should_floor=True, should_cap=True):
    if should_floor:
        frame_no = max(frame_no,0)
    if should_cap:
        total_frames = get_total_frames(cap)
        frame_no = min(total_frames, frame_no)
    
    cur_frame_no = get_cur_frame_no(cap)
    if cur_frame_no != frame_no:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)

def get_next_frame(cap):
    if cap.grab():
        flag, frame = cap.retrieve()
        if flag:
            return frame
    return None

def free_resources(cap):
    cap.release()

def get_fps(cap):
    return cap.get(cv2.CAP_PROP_FPS) if cap else 0

def get_total_frames(cap):
    return int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap else 0
