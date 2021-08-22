import logging
import wave

import pyaudio
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

from number_utils import convert_to_int


class AudioThread(QObject):
    def __init__(self, audio_path, video_fps, signal_to_emit, parent=None):
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit

        self.audio_wave = wave.open(audio_path, 'rb')
        self.pyaudio = pyaudio.PyAudio()
        audio_format = self.pyaudio.get_format_from_width(self.audio_wave.getsampwidth())
        self.audio_stream = self.pyaudio.open(format=audio_format,
                                              channels=self.audio_wave.getnchannels(),
                                              rate=self.audio_wave.getframerate(),
                                              output=True)
        self.video_fps = video_fps

        signal_to_emit.connect(self.play_audio_handler)

    @pyqtSlot(int)
    def play_audio_handler(self, num_of_video_frames):
        logging.debug("play audio")

        audio_frames_to_get = convert_to_int(num_of_video_frames * self.audio_wave.getframerate() / self.video_fps)
        self.audio_stream.write(self.audio_wave.readframes(audio_frames_to_get))


class AudioPlayer(QObject):
    play_audio = pyqtSignal(int)
    audio_path = 'audio.wav'

    def __init__(self, video_path, video_fps):
        super().__init__()

        import subprocess
        command = "ffmpeg -y -i {} -vn {}".format(video_path, self.audio_path)
        subprocess.call(command, shell=True)

        self.worker = AudioThread(self.audio_path, video_fps, self.play_audio)

        thread = QThread(self)
        self.worker.moveToThread(thread)
        thread.start()
