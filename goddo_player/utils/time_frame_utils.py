from math import ceil, floor
import re
import time


def fps_to_num_millis(num_frames):
    return int(round(1000 / num_frames))


def frames_to_secs(no_of_frames, fps):
    return int(round(no_of_frames / fps))


def get_perf_counter_as_millis():
    return int(time.perf_counter() * 1000)


def frames_to_time_components(total_frames, fps):
    hours = floor(total_frames / fps / 60 / 60)
    mins = floor(total_frames / fps / 60) % 60
    secs = floor(total_frames / fps) % 60
    frames = floor(total_frames % fps)
    return hours, mins, secs, frames


def frames_to_time_ms_components(total_frames, fps):
    hours = floor(total_frames / fps / 60 / 60)
    mins = floor(total_frames / fps / 60) % 60
    secs = floor(total_frames / fps) % 60
    ms = floor(total_frames / fps * 1000)
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
# leading - is ignored as it makes no sense in terms of splitting to components
def time_str_to_components(time_str: str):
    cleaned_time_str = time_str if time_str[0] != '-' else time_str[1:]

    idx_of_1st_colon = cleaned_time_str.index(':')
    idx_of_2nd_colon = cleaned_time_str.index(':', idx_of_1st_colon+1)
    idx_of_last_dot = cleaned_time_str.rindex('.')
    hours = int(cleaned_time_str[:idx_of_1st_colon])
    mins = int(cleaned_time_str[idx_of_1st_colon+1:idx_of_2nd_colon])
    secs = int(cleaned_time_str[idx_of_2nd_colon+1:idx_of_last_dot])
    frames = int(cleaned_time_str[idx_of_last_dot+1:])
    return hours, mins, secs, frames

# last component_type is either frames or ms
def time_str_to_frames(time_str: str, fps, last_component_type='frames'):
    hrs, mins, secs, ms_or_frames = time_str_to_components(time_str)

    last_component_total_frames = 0
    if last_component_type.lower() == 'frames':
        last_component_total_frames = ms_or_frames
    elif last_component_type.lower() == 'ms':
        ms = ms_or_frames

        if fps is None or fps == 0:
            raise Exception(f"Please pass correct fps in, we cannot divide by {fps}")
        last_component_total_frames = ms / 1000 * fps

    # frames to str does a floor so here we do the reverse which is ceil
    total_frames = ceil(hrs * 60 * 60 * fps + mins * 60 * fps + secs * fps + last_component_total_frames)
    return total_frames if time_str[0] != '-' else -total_frames

def is_time_label(text):
    return re.match('^[0-9]:[0-9][0-9]:[0-9][0-9]\\.[0-9][0-9]$', text)
