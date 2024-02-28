import pathlib


class PlayerConfigs:
    supported_video_exts = ['.mp4', '.wmv', '.mkv', '.webm', '.avi', '.mov', '.m2ts', '.ts', '.asf', '.flv', 'm4v',
                            '.mpg', '.rmvb']
    timeline_initial_width = 1075
    timeline_initial_width_of_one_min = 120
    timeline_min_width_of_one_min = 30
    timeline_max_width_of_one_min = 600
    timeline_length_of_triangle = 15
    default_extra_frames_in_secs = 10
    audio_thread_pool_size = 1
    default_volume = 1
    max_volume = 1
    max_tags_in_dropdown = 1000

    base_output_folder = pathlib.Path(__file__).parent.parent.parent.joinpath('output')

    # a.json on goddo player's root / saves
    default_save_file = base_output_folder.parent.joinpath('saves').joinpath('a.json').resolve()
    
