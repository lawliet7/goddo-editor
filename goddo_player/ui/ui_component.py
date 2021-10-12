from abc import abstractmethod

from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtGui import QPainter, QMouseEvent


class UiComponent(QObject):
    def __init__(self):
        super().__init__()

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
        return super().event(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pass

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pass

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pass


