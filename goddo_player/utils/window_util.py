from PyQt5.QtCore import QRect
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QApplication, QStyle, QWidget


def get_title_bar_height():
    return QApplication.style().pixelMetric(QStyle.PM_TitleBarHeight)


def move_window(window_instance, x, y):
    if isinstance(window_instance, QWidget):
        window_instance.move(x, y)
    elif isinstance(window_instance, QWindow):
        # opengl windows don't take into account title bar
        window_instance.setX(x)
        window_instance.setY(y+get_title_bar_height())
    else:
        raise Exception("Invalid window type")


def activate_window(window, restore_minimized=True):
    if restore_minimized and window.isMinimized():
        window.showNormal()
    window.activateWindow()


def clone_rect(rect: QRect) -> QRect:
    return QRect(rect.topLeft(), rect.bottomRight())
