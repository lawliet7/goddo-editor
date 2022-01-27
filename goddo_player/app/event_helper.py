import os

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication


def common_event_handling(event, signals, state):
    if event.key() == Qt.Key_Escape:
        QApplication.exit(0)
    elif event.key() == Qt.Key_F2:
        signals.activate_all_windows_slot.emit()
    elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
        url = QUrl.fromLocalFile(os.path.abspath(os.path.join('..', 'saves', 'a.json')))
        signals.save_slot.emit(url)


def is_key_with_modifiers(event, key, ctrl=False, shift=False, numpad=False):
    numpad_bool = (event.modifiers() == Qt.KeypadModifier) if numpad else True
    ctrl_bool = (event.modifiers() == Qt.ControlModifier) if ctrl else True
    shift_bool = (event.modifiers() == Qt.ShiftModifier) if shift else True

    return event.key() == key and numpad_bool and ctrl_bool and shift_bool
