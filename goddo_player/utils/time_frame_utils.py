import time


def fps_to_num_millis(num_frames):
    return int(round(1000 / num_frames))


def frames_to_secs(no_of_frames, fps):
    return int(round(no_of_frames / fps))


def get_perf_counter_as_millis():
    return int(time.perf_counter() * 1000)


def frames_to_time_components(total_frames, fps):
    frames = int(total_frames % fps)
    secs = int(total_frames / fps % 60)
    mins = int(total_frames / fps / 60 % 60)
    hours = int(total_frames / fps / 60 / 60 % 60)
    return hours, mins, secs, frames


def frames_to_time_ms_components(total_frames, fps):
    ms = int(total_frames / fps * 1000)
    secs = int(total_frames / fps % 60)
    mins = int(total_frames / fps / 60 % 60)
    hours = int(total_frames / fps / 60 / 60 % 60)
    return hours, mins, secs, ms


def ms_to_time_components(ms, fps):
    total_secs = ms / 1000

    frames = int((total_secs * fps) % fps)
    secs = int(total_secs % 60)
    mins = int((total_secs / 60) % 60)
    hours = int((total_secs / 60 / 60) % 60)
    return hours, mins, secs, frames


def build_time_str(hours=0, mins=0, secs=0, frames=0):
    return "{}:{:02d}:{:02d}.{:02d}".format(hours, mins, secs, frames)


def build_time_str_least_chars(hours=0, mins=0, secs=0, frames=0):
    if hours > 0:
        return "{}:{:02d}:{:02d}.{:02d}".format(hours, mins, secs, frames)
    elif mins > 0:
        return "{:2d}:{:02d}.{:02d}".format(mins, secs, frames)
    else:
        return "{:2d}.{:02d}".format(secs, frames)


def build_time_ms_str_least_chars(hours=0, mins=0, secs=0, ms=0):
    if hours > 0:
        return "{}:{:02d}:{:02d}.{:03d}".format(hours, mins, secs, ms)
    elif mins > 0:
        return "{:2d}:{:02d}.{:03d}".format(mins, secs, ms)
    else:
        return "{:2d}.{:03d}".format(secs, ms)


# hours, mins, secs, frames
def time_str_to_components(time_str: str):
    return int(time_str[0]), int(time_str[2:4]), int(time_str[5:7]), int(time_str[8:])
