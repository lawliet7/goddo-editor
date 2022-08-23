
import logging
from typing import Callable
import numpy as np
import pyaudio
import shutil
import wave
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot, QTimer
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.state_store import StateStore
from goddo_player.utils.file_utils import is_non_empty_file

from goddo_player.utils.loading_dialog import LoadingDialog
from goddo_player.utils.message_box_utils import show_error_box

class AudioPlayer2(QObject):
    class _AudioLoadThreadSignals(QObject):
        finished = pyqtSignal(str)
        error = pyqtSignal(str)

    class _AudioLoadThread(QRunnable):
        def __init__(self, input_file_path: str, wav_output_file_path: str):
            super().__init__()
            self.input_file_path = input_file_path
            self.wav_output_file_path = wav_output_file_path
            self.signals = AudioPlayer2._AudioLoadThreadSignals()

        def run(self):
            tmp_wav_file_name = self._get_tmp_file_name()

            import subprocess
            command = 'ffmpeg -y -i "{}" -vn "{}"'.format(self.input_file_path, tmp_wav_file_name)
            logging.info(f'running command: {command}')
            process = subprocess.run(command, capture_output=True, text=True)
            logging.info(f'return val: {process}')
            logging.debug('stdout')
            logging.debug(process.stdout)
            logging.debug('stderr')
            logging.debug(process.stderr)
            
            if process.returncode == 0:
                shutil.move(tmp_wav_file_name, self.wav_output_file_path)
                self.signals.finished.emit(self.wav_output_file_path)
            else:
                self.signals.error.emit(process.stderr)

        def _get_tmp_file_name(self):
            from pathlib import Path
            wav_path = Path(self.wav_output_file_path)
            return wav_path.parent.joinpath('wip_'+wav_path.name)

    class _AudioPlaybackThreadSignals(QObject):
        play_audio = pyqtSignal(int, bool)
        goto_audio = pyqtSignal(int)

    class _AudioPlaybackWorker(QObject):
        def __init__(self, pw_state, audio_path):
            super().__init__()
            self.signals = AudioPlayer2._AudioPlaybackThreadSignals()

            self.pw_state = pw_state

            self.audio_wave = wave.open(audio_path, 'rb')
            self.pyaudio = pyaudio.PyAudio()
            audio_format = self.pyaudio.get_format_from_width(self.audio_wave.getsampwidth())
            self.audio_stream = self.pyaudio.open(format=audio_format,
                                                channels=self.audio_wave.getnchannels(),
                                                rate=self.audio_wave.getframerate(),
                                                output=True)
            self.video_fps = self.pw_state.fps

            self.signals.play_audio.connect(self.play_audio_handler)
            self.signals.goto_audio.connect(self.go_to_audio_handler)

            self.go_to_audio_handler(self.pw_state.current_frame_no)

        @pyqtSlot(int, bool)
        def play_audio_handler(self, num_of_video_frames, skip):
            logging.debug("play audio")

            audio_frames_to_get = int(round(num_of_video_frames / self.video_fps * self.audio_wave.getframerate()))
            # for _ in range(num_of_video_frames):
            #     audio_frames_to_get = int(round(self.audio_wave.getframerate() / self.video_fps))

            # if audio_frames_to_get is not None:
            frames = self.audio_wave.readframes(audio_frames_to_get)
            if not skip and frames != '':
                # if self.state.source['volume'] != 1:
                #     frames = (np.frombuffer(frames, dtype=np.int16) * self.state.source['volume']).astype(np.int16).tobytes()
                self.audio_stream.write(frames)

        @pyqtSlot(int)
        def go_to_audio_handler(self, frame):
            audio_frames_to_go = int(round(frame * self.audio_wave.getframerate() / self.video_fps))
            logging.debug(f'{audio_frames_to_go} - {frame} - {self.audio_wave.getframerate()} - {self.video_fps}')
            self.audio_wave.setpos(audio_frames_to_go)

    def __init__(self, is_output_window: bool):
         super().__init__()

         self.pw_state = StateStore().preview_window_output if is_output_window else StateStore().preview_window

         self._dialog = LoadingDialog()
         self._pool = QThreadPool()
         self._pool.setMaxThreadCount(PlayerConfigs.audio_thread_pool_size)
         self.worker = None

    def load_audio(self, video_path: str, wav_output_path: str, fn: Callable = None):
        self._dialog.open_dialog()

        if is_non_empty_file(wav_output_path):
            self._finished_loading(wav_output_path)
            fn(wav_output_path)
        else:
            at = self._AudioLoadThread(video_path, wav_output_path)
            at.signals.finished.connect(self._finished_loading)
            at.signals.error.connect(self._error_loading)

            if fn:
                at.signals.finished.connect(fn)

            self._pool.start(at)

    @pyqtSlot(str)
    def _finished_loading(self, audio_file: str):
        self._dialog.close()
        self.worker = AudioPlayer2._AudioPlaybackWorker(self.pw_state, audio_file)

    @pyqtSlot(str)
    def _error_loading(self, error_msg: str):
        self._dialog.close()
        show_error_box(None, error_msg)
