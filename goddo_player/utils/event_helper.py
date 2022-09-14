from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from goddo_player.utils.message_box_utils import show_error_box


def common_event_handling(event, signals, state) -> bool:
    if is_key_press(event, Qt.Key_Escape):
        QApplication.exit(0)
        event.accept()
    elif is_key_press(event, Qt.Key_F2):
        signals.activate_all_windows_slot.emit('')
        event.accept()
    elif is_key_with_modifiers(event, Qt.Key_S, ctrl=True):
        if not state.cur_save_file.is_empty():
            signals.save_slot.emit(state.cur_save_file)
            event.accept()
        else:
            show_error_box(None, "There's no file loaded")

def get_key_modifiers():
    QModifiers = QApplication.keyboardModifiers()
    modifiers = []
    if (QModifiers & Qt.ShiftModifier) == Qt.ShiftModifier:
        modifiers.append('shift')
    if (QModifiers & Qt.ControlModifier) == Qt.ControlModifier:
        modifiers.append('control')
    if (QModifiers & Qt.AltModifier) == Qt.AltModifier:
        modifiers.append('alt')
    if (QModifiers & Qt.MetaModifier) == Qt.MetaModifier:
        modifiers.append('meta')
    if (QModifiers & Qt.KeypadModifier) == Qt.KeypadModifier:
        modifiers.append('numpad')
    return modifiers

def is_key_with_modifiers(event, key, ctrl=False, shift=False, numpad=False, alt=False, meta=False):
    modifiers = get_key_modifiers()
    numpad_bool = ('numpad' in modifiers) if numpad else True
    ctrl_bool = ('control' in modifiers) if ctrl else True
    shift_bool = ('shift' in modifiers) if shift else True
    alt_bool = ('alt' in modifiers) if alt else True
    meta_bool = ('meta' in modifiers) if meta else True

    return event.key() == key and numpad_bool and ctrl_bool and shift_bool and alt_bool and meta_bool

def is_key_press(event, key):
    modifiers = get_key_modifiers()
    return event.key() == key and (len(modifiers) == 0 or 'numpad' in modifiers)
