from PyQt5.QtWidgets import QMessageBox


def show_error_box(parent, msg, title='Error'):
    QMessageBox.critical(parent, title, msg, QMessageBox.Ok)

def show_info_box(parent, msg, title, buttons=QMessageBox.Ok):
    return QMessageBox.information(parent, title, msg, buttons)
