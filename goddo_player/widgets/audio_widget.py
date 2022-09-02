
from dataclasses import asdict, dataclass
import logging
import os
from pathlib import Path
from typing import Callable
import numpy as np
import pyaudio
import shutil
import subprocess
import wave
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot, QTimer, QThread
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.signals import SignalFunctionId, StateStoreSignals
from goddo_player.app.state_store import StateStore
from goddo_player.utils.file_utils import is_non_empty_file

from goddo_player.utils.loading_dialog import LoadingDialog
from goddo_player.utils.message_box_utils import show_error_box
from goddo_player.utils.video_path import VideoPath

@dataclass(frozen=True)
class AudioDetails:
    audio_path: str
    frame_rate: float
    channels: int
    no_of_frames: int
    sample_width: int
    cur_pos: int

    def as_dict(self):
        return asdict(self)


class _AudioThread(QObject):
    load_slot = pyqtSignal(VideoPath, float, SignalFunctionId) # video path, video fps, function index for callback
    ready_slot = pyqtSignal(str, SignalFunctionId)
    close_slot = pyqtSignal(SignalFunctionId) # function index for callback
    error_slot = pyqtSignal(str)
    play_audio_slot = pyqtSignal(int, float, bool) # num of frames to play, volume, should simply skip the frames
    seek_audio_slot = pyqtSignal(int) # frame no to go to

    def __init__(self):
        super().__init__()

        self.qthread = QThread()
        self.moveToThread(self.qthread)

        self.signals: StateStoreSignals = StateStoreSignals()

        self.pyaudio = pyaudio.PyAudio()

        self.audio_file_path = ''
        self.video_fps = 0
        self.audio_wave = None
        self.audio_stream = None

        self.load_slot.connect(self._load_audio)
        self.play_audio_slot.connect(self.play_audio_handler)
        self.seek_audio_slot.connect(self.seek_audio_handler)
        self.close_slot.connect(self._close_audio)

        self.qthread.start()

    def _get_audio_file_path(self, video_path: VideoPath):
        return os.path.join('output',video_path.file_name(include_ext=False)+'.wav')

    def _get_tmp_file_name(self, audio_file_path: str):
        p = Path(audio_file_path)
        return p.parent.joinpath('wip_'+p.name)

    @pyqtSlot(SignalFunctionId)
    def _close_audio(self, fn_id: SignalFunctionId):
        if self.audio_stream:
            self.audio_stream.close()
            self.audio_wave.close()

            self.audio_wave = None
            self.audio_stream = None
            self.video_fps = 0
        logging.info('super closing audio da ze')
        self.signals.fn_repo.pop(fn_id)()

    # @pyqtSlot(VideoPath, float, SignalFunctionId)
    def _load_audio(self, video_path: VideoPath, video_fps: float, fn_id: SignalFunctionId):
        logging.info(f'emitting close slot')
        self.close_slot.emit(SignalFunctionId.no_function())
        logging.info(f'finished emitting close slot')

        audio_file_path = self._get_audio_file_path(video_path)

        if not is_non_empty_file(audio_file_path):
            tmp_wav_file_name = self._get_tmp_file_name(audio_file_path)

            command = 'ffmpeg -y -i "{}" -vn "{}"'.format(video_path.str(), tmp_wav_file_name)
            logging.info(f'running command: {command}')

            process = subprocess.run(command, capture_output=True, text=True)

            logging.info(f'return val: {process}')
            logging.debug('stdout')
            logging.debug(process.stdout)
            logging.debug('stderr')
            logging.debug(process.stderr)
            
            if process.returncode != 0:
                self.error_slot.emit(process.stderr)
                return

            shutil.move(tmp_wav_file_name, audio_file_path)

        self.audio_file_path = audio_file_path

        self.audio_wave = wave.open(audio_file_path, 'rb')
        self.audio_stream = self.pyaudio.open(format=self.pyaudio.get_format_from_width(self.audio_wave.getsampwidth()),
                                            channels=self.audio_wave.getnchannels(),
                                            rate=self.audio_wave.getframerate(),
                                            output=True)
        self.video_fps = video_fps
        
        self.ready_slot.emit(audio_file_path, fn_id)

    @pyqtSlot(int, float, bool)
    def play_audio_handler(self, num_of_video_frames: int, volume: float, skip: bool):
        logging.debug("play audio")

        audio_frames_to_get = int(round(num_of_video_frames / self.video_fps * self.audio_wave.getframerate()))
        frames = self.audio_wave.readframes(audio_frames_to_get)
        if not skip and frames != '':
            if volume != 1:
                frames = (np.frombuffer(frames, dtype=np.int16) * volume).astype(np.int16).tobytes()
            self.audio_stream.write(frames)

    @pyqtSlot(int)
    def seek_audio_handler(self, frame: int):
        audio_frames_to_go = int(round(frame * self.audio_wave.getframerate() / self.video_fps))
        logging.debug(f'{audio_frames_to_go} - {frame} - {self.audio_wave.getframerate()} - {self.video_fps}')
        self.audio_wave.setpos(audio_frames_to_go)
        

    def get_audio_details(self) -> AudioDetails:
        if self.has_active_audio():
            return AudioDetails(
                audio_path=self.audio_file_path,
                frame_rate=self.audio_wave.getframerate(),
                channels=self.audio_wave.getnchannels(),
                no_of_frames=self.audio_wave.getnframes(),
                sample_width=self.audio_wave.getsampwidth(),
                cur_pos=self.audio_wave.tell(),
            )
        else:
            return None

    def has_active_audio(self) -> bool:
        return self.audio_wave is not None

class AudioPlayer(QObject):
    def __init__(self):
        super().__init__()

        self.signals: StateStoreSignals = StateStoreSignals()

        self.audio_thread = _AudioThread()

        self.play_audio_slot = self.audio_thread.play_audio_slot
        self.seek_audio_slot = self.audio_thread.seek_audio_slot
        self.audio_thread.ready_slot.connect(self._finished_loading)
        self.audio_thread.error_slot.connect(self._error_loading)

        self._dialog = LoadingDialog()

    def is_dialog_closed(self):
        return self._dialog.isHidden()

    def load_audio(self, video_path: VideoPath, video_fps: float, fn: Callable[[str], None] = None):
        self._dialog.open_dialog()

        if not video_path.is_empty():
            fn_id = self.signals.fn_repo.push(fn) if fn else SignalFunctionId.no_function()
            self.audio_thread.load_slot.emit(video_path, video_fps, fn_id)
        else:
            fn_id = self.signals.fn_repo.push(fn) if fn else SignalFunctionId.no_function()
            self.audio_thread.close_slot.emit(fn_id)

    @pyqtSlot(str, SignalFunctionId)
    def _finished_loading(self, audio_file: str, fn_id: SignalFunctionId):
        self.signals.fn_repo.pop(fn_id)(audio_file)
        self._dialog.close()

    @pyqtSlot(str)
    def _error_loading(self, error_msg: str):
        self._dialog.close()
        show_error_box(None, error_msg)

    def get_audio_details(self) -> AudioDetails:
        return self.audio_thread.get_audio_details()

    def has_active_audio(self) -> bool:
        return self.audio_thread.has_active_audio()
