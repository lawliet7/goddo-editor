from PyQt5.QtWidgets import QMessageBox, QInputDialog


def show_error_box(parent, msg, title='Error'):
    QMessageBox.critical(parent, title, msg, QMessageBox.Ok)

def show_info_box(parent, msg, title, buttons=QMessageBox.Ok):
    return QMessageBox.information(parent, title, msg, buttons)

def show_input_msg_box(parent, msg, title):
    return QInputDialog.getText(parent, title, msg)
