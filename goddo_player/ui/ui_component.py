from abc import abstractmethod
from typing import Callable

from PyQt5.QtCore import QObject, QEvent, QRect
from PyQt5.QtGui import QPainter, QMouseEvent, QKeyEvent, QDragEnterEvent, QWindow, QPaintDeviceWindow, QWheelEvent


def get_window(obj: QObject) -> QPaintDeviceWindow:
    if obj is None:
        raise Exception("no window found in object hierarchy")
    elif isinstance(obj, QPaintDeviceWindow):
        return obj
    else:
        return get_window(obj.parent())


class UiComponent(QObject):
    def __init__(self, parent, get_rect):
        super().__init__(parent=parent)

        self.window: QPaintDeviceWindow = get_window(self)

        self.get_rect: Callable[[], QRect] = get_rect

    def __get_child_ui_components(self):
        return [x for x in vars(self).values() if isinstance(x, UiComponent)]

    # @abstractmethod
    def paint(self, painter: QPainter):
        child_components = [x for x in vars(self).values() if isinstance(x, UiComponent)]
        for c in child_components:
            c.paint(painter)

    def event(self, event: QEvent) -> bool:
        child_components = [x for x in vars(self).values() if isinstance(x, UiComponent)]
        for c in child_components:
            c.event(event)

        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
        elif event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
        elif event.type() == QEvent.MouseButtonRelease:
            self.mouseReleaseEvent(event)
        elif event.type() == QKeyEvent.KeyPress:
            self.keyPressEvent(event)
        elif event.type() == QEvent.Enter:
            self.mouseEnterEvent(event)
        elif event.type() == QEvent.Leave:
            self.mouseLeaveEvent(event)
        elif event.type() == QEvent.Wheel:
            self.mouseWheelEvent(event)
        elif event.type() == QEvent.DragEnter:
            self.dragEnterEvent(event)
        elif event.type() == QEvent.Drop:
            self.onDropEvent(event)
        else:
            return super().event(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pass

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pass

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pass

    def mouseWheelEvent(self, event: QWheelEvent) -> None:
        pass

    def keyPressEvent(self, event: QKeyEvent) -> None:
        pass

    def mouseEnterEvent(self, event: QEvent) -> None:
        pass

    def mouseLeaveEvent(self, event: QEvent) -> None:
        pass

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        pass

    def onDropEvent(self, event: QDragEnterEvent) -> None:
        pass

