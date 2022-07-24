import logging
import re
import typing
from PyQt5.QtGui import QValidator, QWheelEvent, QKeyEvent
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtCore import Qt
from goddo_player.utils.event_helper import is_key_press

from goddo_player.utils.time_frame_utils import time_str_to_components, time_str_to_frames


class TimeInFramesEdit(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._fps = 0
        self._is_fps_fraction = False

        self.setMaximum(1)
        self.setMinimum(1)

        self._hour_right = self.fontMetrics().width("0:")
        self._min_right = self._hour_right + self.fontMetrics().width("00:")
        self._sec_right = self._min_right + self.fontMetrics().width("00.")

        self.is_valid = True

    def reset(self, fps, current_frame, min_frame, max_frame):
        self._fps = fps
        self._is_fps_fraction = True if abs(self._fps - round(self._fps)) > 0.000001 else False
        self.setMinimum(min_frame)
        self.setMaximum(max_frame)
        self.setValue(current_frame)
        self.is_valid = True

    def valueFromText(self, text: str) -> int:
        return time_str_to_frames(text, self._fps)

    def textFromValue(self, total_frames: int) -> str:
        if self._fps > 0:
            frames = int(total_frames % self._fps)
            secs = int(total_frames / self._fps % 60)
            mins = int(total_frames / self._fps / 60 % 60)
            hours = int(total_frames / self._fps / 60 / 60 % 60)
            return "{}:{:02d}:{:02d}.{:02d}".format(hours, mins, secs, frames)
        else:
            return "0:00:00.00"

    def validate(self, input: str, pos: int) -> typing.Tuple[QValidator.State, str, int]:
        good_style_sheet = 'background-color: white;'
        fail_style_sheet = 'background-color: rgba(255,0,0,0.5);'

        if re.match('^[0-9]:[0-5][0-9]:[0-5][0-9]\\.[0-9][0-9]$', input):
            fps_section = int(input[-2:])
            logging.debug(f'=== validate fps {fps_section} - {int(round(self._fps))}')
            if fps_section >= int(round(self._fps)):
                logging.debug('validate failed')
                self.setStyleSheet(fail_style_sheet)
                self.is_valid = False
                return QValidator.Intermediate, input, pos
            elif self.minimum() > self.valueFromText(input) or self.maximum() < self.valueFromText(input):
                logging.debug('validate intermediate')
                self.setStyleSheet(fail_style_sheet)
                self.is_valid = False
                return QValidator.Intermediate, input, pos
            elif self._is_fps_fraction and fps_section == int(round(self._fps))-1:
                logging.debug(f'checking if fps is valid success {input}')
                frame = self.valueFromText(input)
                reconstructed_label = self.textFromValue(frame)

                if reconstructed_label == input:
                    self.setStyleSheet(good_style_sheet)
                    self.is_valid = True
                    return QValidator.Acceptable, input, pos
                else:
                    self.setStyleSheet(fail_style_sheet)
                    self.is_valid = False
                    return QValidator.Intermediate, input, pos
            else:
                logging.debug(f'validate success {input}')
                self.setStyleSheet(good_style_sheet)
                self.is_valid = True
                return QValidator.Acceptable, input, pos
        elif re.match('^[0-9]?:[0-9]{0,2}:[0-9]{0,2}\\.[0-9]{0,2}$', input):
            logging.debug('validate intermediate')
            self.setStyleSheet(fail_style_sheet)
            self.is_valid = False
            return QValidator.Intermediate, input, pos
        else:
            logging.debug('validate failed')
            return QValidator.Invalid, input, pos

    def wheelEvent(self, event: QWheelEvent):
        logging.debug(f'wheel {event}')
        
        self._hour_right

        x = event.pos().x()
        if x <= self._hour_right:
            logging.debug('increment hour')
            offset = int(round(60 * 60 * self._fps))
        elif x <= self._min_right:
            logging.debug('increment min')
            offset = int(round(60 * self._fps))
        elif x <= self._sec_right:
            logging.debug('increment sec')
            offset = int(round(self._fps))
        else:
            logging.debug('increment ms')
            offset = 1

        if event.angleDelta().y() > 0:
            self.setValue(self.value() + offset)
        else:
            self.setValue(self.value() - offset)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if is_key_press(event, Qt.Key_Up) or is_key_press(event, Qt.Key_Down):
            cursor_pos = self.lineEdit().cursorPosition()

            idx_of_1st_colon = self.text().index(':')
            idx_of_2nd_colon = self.text().index(':', idx_of_1st_colon+1)
            idx_of_last_dot = self.text().rindex('.')

            if cursor_pos <= idx_of_1st_colon:
                logging.debug('increment hour')
                offset = int(round(60 * 60 * self._fps))
            elif cursor_pos <= idx_of_2nd_colon:
                logging.debug('increment min')
                offset = int(round(60 * self._fps))
            elif cursor_pos <= idx_of_last_dot:
                logging.debug('increment sec')
                offset = int(round(self._fps))
            else:
                logging.debug('increment ms')
                offset = 1

            if is_key_press(event, Qt.Key_Up):
                self.setValue(self.value() + offset)
            else:
                self.setValue(self.value() - offset)
        elif is_key_press(event, Qt.Key_Return) or is_key_press(event, Qt.Key_Enter):
            if self.is_valid:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
