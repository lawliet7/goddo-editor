from typing import List, Tuple
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QPushButton


def show_error_box(parent, msg, title='Error'):
    QMessageBox.critical(parent, title, msg, QMessageBox.Ok)

def show_info_box(parent, msg, title, buttons=QMessageBox.Ok):
    return QMessageBox.information(parent, title, msg, buttons)

def show_input_msg_box(parent, msg, title, default_text=''):
    return QInputDialog.getText(parent, title, msg, text=default_text)

def show_custom_msg_box(parent, icon: QMessageBox.Icon, title: str, msg: str, btns: List[Tuple[str,QMessageBox.ButtonRole]]) -> Tuple[QMessageBox,List[QPushButton]]:
    msg_box = QMessageBox(icon=icon, title=title, msg=msg, parent=parent)

    btn_ids = []
    for (btn_txt,btn_action) in btns:
        btn_ids.append(msg_box.addButton(btn_txt, btn_action))
    msg_box.exec_()

    return msg_box, btn_ids
