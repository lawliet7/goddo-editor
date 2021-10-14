import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget, QApplication


class SliderWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(10, 50, 800, 600)
        self.setWindowTitle('Icon')

        self.rect_height = 28
        self.x_margin = 385
        self.y_margin = 10
        self.x_radius = 5
        self.y_radius = 5

        self.rect = QRect(0, self.geometry().height() - self.rect_height, self.geometry().width(), self.rect_height)
        self.button_width = self.rect.width()-self.x_margin*2
        self.x = 2
        self.mouse_down = False

    @property
    def button_rect(self):
        return QRect(self.x, self.rect.y() + self.y_margin,
                     self.button_width, self.rect.height() - self.y_margin * 2)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Q:
            print("up")
            self.rect_height = min(self.geometry().height(), self.rect_height+1)
            self.update()
            event.accept()
        elif event.key() == Qt.Key_A:
            print("down")
            self.rect_height = max(0, self.rect_height - 1)
            self.update()
            event.accept()
        elif event.key() == Qt.Key_W:
            print("up")
            self.x_margin = max(1, self.x_margin - 1)
            self.update()
            event.accept()
        elif event.key() == Qt.Key_S:
            print("down")
            self.x_margin = min(int(self.geometry().width() / 2), self.x_margin + 1)
            self.update()
            event.accept()
        elif event.key() == Qt.Key_E:
            print("up")
            self.y_margin = max(1, self.y_margin - 1)
            self.update()
            event.accept()
        elif event.key() == Qt.Key_D:
            print("down")
            self.y_margin = min(int(self.rect_height/ 2), self.y_margin + 1)
            self.update()
            event.accept()
        elif event.key() == Qt.Key_R:
            print("up")
            self.x_radius = max(1, self.x_radius - 1)
            self.update()
            event.accept()
        elif event.key() == Qt.Key_F:
            print("down")
            self.x_radius = min(90, self.x_radius + 1)
            self.update()
            event.accept()
        elif event.key() == Qt.Key_T:
            print("up")
            self.y_radius = max(1, self.y_radius - 1)
            self.update()
            event.accept()
        elif event.key() == Qt.Key_G:
            print("down")
            self.y_radius = min(90, self.y_radius + 1)
            self.update()
            event.accept()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        print(event.pos())
        print(self.rect)
        print(self.button_width)
        if self.rect.contains(event.pos()):
            self.x = event.pos().x() - self.button_width / 2
            self.x = max(2, self.x)
            print(f"x={self.x} min={self.rect.width() - self.button_width / 2}")
            self.x = min(self.rect.width() - self.button_width - 2, self.x)
            print(self.x)
            self.mouse_down = True
            self.update()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_down = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mouse_down:
            self.x = event.pos().x() - self.button_width / 2
            self.x = max(2, self.x)
            print(f"x={self.x} min={self.rect.width() - self.button_width / 2}")
            self.x = min(self.rect.width() - self.button_width - 2, self.x)
            print(self.x)
            self.update()
        else:
            super().mouseMoveEvent(event)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        print("paint")

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(QColor("black")))
        print(f'rect height {self.rect_height}')

        # painter.drawRect(self.rect)

        print(f'x margin {self.x_margin}')
        print(f'y margin {self.y_margin}')
        print(f'x radius {self.x_radius}')
        print(f'y radius {self.y_radius}')
        painter.setPen(QPen(QColor("red")))
        painter.drawRoundedRect(self.button_rect, self.x_radius, self.y_radius)

        painter.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SliderWindow()
    ex.show()
    sys.exit(app.exec_())
