import time


def num_frames_to_num_millis(num_frames):
    return int(round(1000 / num_frames))


def get_perf_counter_as_millis():
    return int(time.perf_counter() * 1000)


def frames_to_time_components(total_frames, fps):
    frames = int(total_frames % fps)
    secs = int(total_frames / fps % 60)
    mins = int(total_frames / fps / 60 % 60)
    hours = int(total_frames / fps / 60 / 60 % 60)
    return hours, mins, secs, frames


def ms_to_time_components(ms, fps):
    total_secs = ms / 1000

    frames = int((total_secs * fps) % fps)
    secs = int(total_secs % 60)
    mins = int((total_secs / 60) % 60)
    hours = int((total_secs / 60 / 60) % 60)
    return hours, mins, secs, frames


def build_time_str(hours=0, mins=0, secs=0, frames=0):
    return "{}:{:02d}:{:02d}.{:03d}".format(hours, mins, secs, frames)


def format_time(hour, min, sec, ms):
    return "{}:{:02d}:{:02d}.{:02d}".format(hour, min, sec, ms)