# importing libraries
import re
import typing
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys

from goddo_player.utils.time_frame_utils import time_str_to_components
  
class Window(QMainWindow):
  
    def __init__(self):
        super().__init__()
  
        # setting title
        self.setWindowTitle("Python ")
  
        # setting geometry
        self.setGeometry(100, 100, 600, 400)
  
        # calling method
        self.UiComponents()
  
        # showing all the widgets
        self.show()
  
    # method for widgets
    def UiComponents(self):
  
        # creating spin box
        self.spin = MyQSpinBox(30, self)
        self.spin.editingFinished.connect(self.done)
  
        # setting geometry to spin box
        self.spin.setGeometry(100, 100, 150, 40)
  
        # creating a push button
        button = QPushButton("Click", self)
  
        # setting geometry to the button
        # button.setGeometry(200, 200, 100, 40)
  
        # adding action ot the push button
        # button.pressed.connect(self.do_something)
  
    # # action called by the button
    # def do_something(self):
    #     # closing the spin box
    #     self.spin.close()

    def done(self):
        print(f'you got it, focus={self.spin.hasFocus()}')

class MyQSpinBox(QSpinBox):
    def __init__(self, fps, parent=None):
        super().__init__(parent)

        self.fps = fps

        self.setMaximum(1000000)
        self.setMinimum(0)

        self._hour_right = self.fontMetrics().width("0:")
        self._min_right = self._hour_right + self.fontMetrics().width("00:")
        self._sec_right = self._min_right + self.fontMetrics().width("00.")


    def valueFromText(self, text: str) -> int:
        print('valueFromText')
        hour, min, secs, frames = time_str_to_components(text)
        return int(round(hour * 60 * 60 * self.fps + min * 60 * self.fps + secs * self.fps + frames))

    def textFromValue(self, total_frames: int) -> str:
        frames = int(total_frames % self.fps)
        secs = int(total_frames / self.fps % 60)
        mins = int(total_frames / self.fps / 60 % 60)
        hours = int(total_frames / self.fps / 60 / 60 % 60)
        return "{}:{:02d}:{:02d}.{:02d}".format(hours, mins, secs, frames)

    def validate(self, input: str, pos: int) -> typing.Tuple[QtGui.QValidator.State, str, int]:
        if re.match('^[0-9]+:[0-5][0-9]:[0-5][0-9]\\.[0-9][0-9]$', input):
            if int(input[input.rindex('.')+1:]) >= self.fps:
                print('validate failed')
                return QtGui.QValidator.Invalid, input, pos
            elif self.valueFromText(input) > self.maximum():
                print('validate failed')
                return QtGui.QValidator.Invalid, input, pos
            else:
                print('validate success')
                return QtGui.QValidator.Acceptable, input, pos
        elif re.match('^[0-9]?:[0-9]{1,2}:[0-9]{1,2}\\.[0-9]{1,2}$', input):
            print('validate intermediate')
            return QtGui.QValidator.Intermediate, input, pos
        else:
            print('validate failed')
            return QtGui.QValidator.Invalid, input, pos

    def wheelEvent(self, event: QWheelEvent):
        print(f'wheel pos={event.pos()} global_pos={event.globalPos()}')
        # super.wheelEvent(event)

        x = event.pos().x()
        if x <= self._hour_right:
            print('increment hour')
            offset = int(round(60 * 60 * self.fps))
        elif x <= self._min_right:
            print('increment min')
            offset = int(round(60 * self.fps))
        elif x <= self._sec_right:
            print('increment sec')
            offset = int(round(self.fps))
        else:
            print('increment ms')
            offset = 1

        if event.angleDelta().y() > 0:
            self.setValue(self.value() + offset)
        else:
            self.setValue(self.value() - offset)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Up:
            print(self.cursor().pos())
            print(self.lineEdit().cursorPosition())

            cursor_pos = self.lineEdit().cursorPosition()

            idx_of_1st_colon = self.text().index(':')
            idx_of_2nd_colon = self.text().index(':', idx_of_1st_colon+1)
            idx_of_last_dot = self.text().rindex('.')

            if cursor_pos <= idx_of_1st_colon:
                print('increment hour')
                offset = int(round(60 * 60 * self.fps))
            elif cursor_pos <= idx_of_2nd_colon:
                print('increment min')
                offset = int(round(60 * self.fps))
            elif cursor_pos <= idx_of_last_dot:
                print('increment sec')
                offset = int(round(self.fps))
            else:
                print('increment ms')
                offset = 1

            self.setValue(self.value() + offset)

        elif event.key() == Qt.Key_Down:
            pass
        else:
            super().keyPressEvent(event)

  
# create pyqt5 app
App = QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
  
# start the app
sys.exit(App.exec())