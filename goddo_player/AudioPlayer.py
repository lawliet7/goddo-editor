import logging
import wave

import pyaudio
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

from number_utils import convert_to_int


class AudioSignals(QObject):
    play_audio = pyqtSignal(int)
    goto_audio = pyqtSignal(int)


class AudioThread(QObject):
    def __init__(self, audio_path, video_fps, parent=None):
        super().__init__(parent)
        self.signals = AudioSignals()

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

    @pyqtSlot(int)
    def play_audio_handler(self, num_of_video_frames):
        logging.debug("play audio")

        audio_frames_to_get = None
        for _ in range(num_of_video_frames):
            audio_frames_to_get = convert_to_int(self.audio_wave.getframerate() / self.video_fps)

        if audio_frames_to_get is not None:
            self.audio_stream.write(self.audio_wave.readframes(audio_frames_to_get))

    @pyqtSlot(int)
    def go_to_audio_handler(self, frame):
        logging.debug("go to audio")

        audio_frames_to_go = convert_to_int(frame * self.audio_wave.getframerate() / self.video_fps)
        self.audio_wave.setpos(audio_frames_to_go)


class AudioPlayer(QObject):
    audio_path = 'audio.wav'

    def __init__(self, video_path, video_fps):
        super().__init__()

        import subprocess
        command = "ffmpeg -y -i {} -vn {}".format(video_path, self.audio_path)
        subprocess.call(command, shell=True)

        self.worker = AudioThread(self.audio_path, video_fps)

        thread = QThread(self)
        self.worker.moveToThread(thread)
        thread.start()

    def emit_play_audio_signal(self, num_of_frames):
        self.worker.signals.play_audio.emit(num_of_frames)

    def emit_go_to_audio_signal(self, frame_no):
        self.worker.signals.goto_audio.emit(frame_no)
