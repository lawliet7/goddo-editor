
import logging
from typing import Callable
import numpy as np
import pyaudio
import wave
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot, QTimer
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.state_store import StateStore

from goddo_player.utils.loading_dialog import LoadingDialog

class AudioPlayer2(QObject):
    class _AudioLoadThreadSignals(QObject):
        finished = pyqtSignal(str)

    class _AudioLoadThread(QRunnable):
        def __init__(self, src, dest):
            super().__init__()
            self.src = src
            self.dest = dest
            self.signals = AudioPlayer2._AudioLoadThreadSignals()

        def run(self):
            import subprocess
            command = "ffmpeg -y -i {} -vn {}".format(self.src, self.dest)
            subprocess.call(command, shell=True)
            self.signals.finished.emit(self.dest)

    class _AudioPlaybackThreadSignals(QObject):
        play_audio = pyqtSignal(int, bool)
        goto_audio = pyqtSignal(int)

    class _AudioPlaybackWorker(QObject):
        def __init__(self, state, audio_path):
            super().__init__()
            self.signals = AudioPlayer2._AudioPlaybackThreadSignals()

            self.state = state

            self.audio_wave = wave.open(audio_path, 'rb')
            self.pyaudio = pyaudio.PyAudio()
            audio_format = self.pyaudio.get_format_from_width(self.audio_wave.getsampwidth())
            self.audio_stream = self.pyaudio.open(format=audio_format,
                                                channels=self.audio_wave.getnchannels(),
                                                rate=self.audio_wave.getframerate(),
                                                output=True)
            self.video_fps = self.state.preview_window.fps

            self.signals.play_audio.connect(self.play_audio_handler)
            self.signals.goto_audio.connect(self.go_to_audio_handler)

            self.go_to_audio_handler(self.state.preview_window.current_frame_no)

        @pyqtSlot(int, bool)
        def play_audio_handler(self, num_of_video_frames, skip):
            logging.debug("play audio")

            audio_frames_to_get = None
            for _ in range(num_of_video_frames):
                audio_frames_to_get = int(round(self.audio_wave.getframerate() / self.video_fps))

            if audio_frames_to_get is not None:
                frames = self.audio_wave.readframes(audio_frames_to_get)
                if not skip:
                    if self.state.source['volume'] != 1:
                        frames = (np.frombuffer(frames, dtype=np.int16) * self.state.source['volume']).astype(np.int16).tobytes()
                    self.audio_stream.write(frames)

        @pyqtSlot(int)
        def go_to_audio_handler(self, frame):
            audio_frames_to_go = int(round(frame * self.audio_wave.getframerate() / self.video_fps))
            logging.debug(f'{audio_frames_to_go} - {frame} - {self.audio_wave.getframerate()} - {self.video_fps}')
            self.audio_wave.setpos(audio_frames_to_go)

    def __init__(self):
         super().__init__()

         self.state = StateStore()

         self._dialog = LoadingDialog()
         self._pool = QThreadPool()
         self._pool.setMaxThreadCount(PlayerConfigs.audio_thread_pool_size)

    def load_audio(self, video_path: str, wav_output_path: str, fn: Callable = None):
            """Long-running task in 5 steps."""
            self._dialog.open_dialog()

            at = self._AudioLoadThread(video_path, wav_output_path)
            at.signals.finished.connect(self._finished_loading)

            if fn:
                at.signals.finished.connect(fn)

            self._pool.start(at)

    @pyqtSlot(str)
    def _finished_loading(self, audio_file: str):
        self._dialog.close()
        self.worker = AudioPlayer2._AudioPlaybackWorker(self.state, audio_file)
