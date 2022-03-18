from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from goddo_player.utils.message_box_utils import show_error_box


def common_event_handling(event, signals, state) -> bool:
    if event.key() == Qt.Key_Escape:
        QApplication.exit(0)
        event.accept()
    elif event.key() == Qt.Key_F2:
        signals.activate_all_windows_slot.emit()
        event.accept()
    elif is_key_with_modifiers(event, Qt.Key_S, ctrl=True):
        if not state.cur_save_file.is_empty():
            signals.save_slot.emit(state.cur_save_file)
            event.accept()
        else:
            show_error_box(None, "There's no file loaded")


def is_key_with_modifiers(event, key, ctrl=False, shift=False, numpad=False):
    numpad_bool = (event.modifiers() == Qt.KeypadModifier) if numpad else True
    ctrl_bool = (event.modifiers() == Qt.ControlModifier) if ctrl else True
    shift_bool = (event.modifiers() == Qt.ShiftModifier) if shift else True

    return event.key() == key and numpad_bool and ctrl_bool and shift_bool
