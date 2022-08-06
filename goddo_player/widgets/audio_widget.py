
from typing import Callable
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot, QTimer
from goddo_player.app.player_configs import PlayerConfigs

from goddo_player.utils.loading_dialog import LoadingDialog

class AudioPlayer2(QObject):
    finished_loading_slot = pyqtSignal()

    class _AudioThreadSignals(QObject):
        finished = pyqtSignal()

    class _AudioThread(QRunnable):

        def __init__(self, src, dest):
            super().__init__()
            self.src = src
            self.dest = dest
            self.signals = AudioPlayer2._AudioThreadSignals()

        def run(self):
            import subprocess
            command = "ffmpeg -y -i {} -vn {}".format(self.src, self.dest)
            subprocess.call(command, shell=True)
            self.signals.finished.emit()

    def __init__(self):
         super().__init__()

         self._dialog = LoadingDialog()
         self._pool = QThreadPool()
         self._pool.setMaxThreadCount(PlayerConfigs.audio_thread_pool_size)

    def load_audio(self, video_path: str, wav_output_path: str, fn: Callable = None):
            """Long-running task in 5 steps."""
            self._dialog.open_dialog()

            at = self._AudioThread(video_path, wav_output_path)
            at.signals.finished.connect(self._finished_loading)

            if fn:
                at.signals.finished.connect(fn)

            self._pool.start(at)

    def _finished_loading(self):
        self._dialog.close()
