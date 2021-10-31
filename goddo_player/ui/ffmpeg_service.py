import json
import subprocess

class FFmpegProcess:
    def __init__(self, piped_process):
        self.pipe

class FFmpegService:
    def __init__(self):
        pass

    @staticmethod
    def probe(path):
        # ffprobe -print_format json -show_streams -v quiet
        args = [
            "ffprobe",
            "-print_format",
            "json",
            "-show_streams",
            "-sexagesimal",
            "-v",
            "quiet",
            "-i",
            path,
        ]

        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        json_data = result.stdout.decode('utf-8')
        result_dict = json.loads(json_data)

        # todo if this doesnt give nb_frames (like wmv) then run this command
        # ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -print_format json -i ...

        video_stream = None
        # audio_stream = None
        for stream in result_dict['streams']:
            if video_stream is None and stream['codec_type'] == 'video':
                video_stream = stream
                break
            # elif audio_stream is None and stream['codec_type'] == 'audio':
            #     audio_stream = stream

        video_dict = {
            "width": video_stream["width"],
            "height": video_stream["height"],
            "fps": FFmpegService.__parse_fps(video_stream['r_frame_rate'] or video_stream['avg_frame_rate']),
            # "total_frames": video_stream.getOrDefault('nb_frames',-1),
            "duration": video_stream['duration'],
        }
        # audio_dict = {
        #
        # }
        # return (video_dict, audio_dict)
        return video_dict

    @staticmethod
    def __parse_fps(fps_str: str) -> float:
        n, d = fps_str.split('/')
        return int(n) / int(d)
