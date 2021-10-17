from abc import abstractmethod
from typing import Callable

from PyQt5.QtCore import QObject, QEvent, QRect
from PyQt5.QtGui import QPainter, QMouseEvent, QKeyEvent


class UiComponent(QObject):
    def __init__(self, screen_update_fn, get_rect):
        super().__init__()

        self.screen_update = screen_update_fn
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
        else:
            return super().event(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pass

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pass

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pass

    def keyPressEvent(self, event: QKeyEvent) -> None:
        pass

    def mouseEnterEvent(self, event: QEvent) -> None:
        pass

    def mouseLeaveEvent(self, event: QEvent) -> None:
        pass


