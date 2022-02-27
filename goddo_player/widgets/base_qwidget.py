from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QWidget

from goddo_player.app.event_helper import common_event_handling


class BaseQWidget(QWidget):
    def __init__(self, *args, **kwrds):
        super().__init__(*args, **kwrds)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        common_event_handling(event, self.signals, self.state)

        if not event.isAccepted():
            super().keyPressEvent(event)
