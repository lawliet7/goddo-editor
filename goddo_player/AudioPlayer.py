import logging
import wave
import numpy as np


import pyaudio
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

from number_utils import convert_to_int


class AudioSignals(QObject):
    play_audio = pyqtSignal(int, bool)
    goto_audio = pyqtSignal(int)


class AudioThread(QObject):
    def __init__(self, state, audio_path, video_fps, parent=None):
        super().__init__(parent)
        self.signals = AudioSignals()

        self.state = state

        self.audio_wave = wave.open(audio_path, 'rb')
        self.pyaudio = pyaudio.PyAudio()
        audio_format = self.pyaudio.get_format_from_width(self.audio_wave.getsampwidth())
        self.audio_stream = self.pyaudio.open(format=audio_format,
                                              channels=self.audio_wave.getnchannels(),
                                              rate=self.audio_wave.getframerate(),
                                              output=True)
        self.video_fps = video_fps

        self.signals.play_audio.connect(self.play_audio_handler)
        self.signals.goto_audio.connect(self.go_to_audio_handler)

        self.go_to_audio_handler(self.state.source['position'])

    @pyqtSlot(int, bool)
    def play_audio_handler(self, num_of_video_frames, skip):
        logging.debug("play audio")

        audio_frames_to_get = None
        for _ in range(num_of_video_frames):
            audio_frames_to_get = convert_to_int(self.audio_wave.getframerate() / self.video_fps)

        if audio_frames_to_get is not None:
            frames = self.audio_wave.readframes(audio_frames_to_get)
            if not skip:
                if self.state.source['volume'] != 1:
                    frames = (np.frombuffer(frames, dtype=np.int16) * self.state.source['volume']).astype(np.int16).tobytes()
                self.audio_stream.write(frames)

    @pyqtSlot(int)
    def go_to_audio_handler(self, frame):
        audio_frames_to_go = convert_to_int(frame * self.audio_wave.getframerate() / self.video_fps)
        logging.debug(f'{audio_frames_to_go} - {frame} - {self.audio_wave.getframerate()} - {self.video_fps}')
        self.audio_wave.setpos(audio_frames_to_go)


class AudioPlayer(QObject):
    audio_path = 'audio.wav'

    def __init__(self, state, video_fps):
        super().__init__()

        self.state = state
        import subprocess
        command = "ffmpeg -y -i {} -vn {}".format(self.state.video_path, self.audio_path)
        subprocess.call(command, shell=True)

        self.worker = AudioThread(self.state, self.audio_path, video_fps)

        thread = QThread(self)
        self.worker.moveToThread(thread)
        thread.start()

    @property
    def volume(self):
        return self.state.source['volume']

    @volume.setter
    def volume(self, volume):
        self.state.source['volume'] = volume

    def emit_play_audio_signal(self, num_of_frames, skip=False):
        self.worker.signals.play_audio.emit(num_of_frames, skip)

    def emit_go_to_audio_signal(self, frame_no):
        self.worker.signals.goto_audio.emit(frame_no)
