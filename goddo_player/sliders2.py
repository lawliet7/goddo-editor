import math
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QRect, Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPolygon
from PyQt5.QtWidgets import QWidget, QApplication


class VolumeControl(QWidget):
    def __init__(self):
        super().__init__()

        # self.setGeometry(10, 60, 1024, 768)
        # self.setWindowTitle('Icon')

        self.text_rect: QRect = None
        self.slider_rect: QRect = None
        self.precise_slider_rect: QRect = None
        self.icon_rect: QRect = None
        self.mute = False
        self.volume = 1
        self.mouse_down_volume = False

        print(self.geometry())
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        print("paint")

        height = 50
        top = self.geometry().height() - height
        # self.rect = QRect(0, top, self.geometry().width(), height)

        text_width = 70
        self.text_rect = QRect(self.geometry().width() - text_width, top, text_width, height)

        slider_width = 100
        self.slider_rect = QRect(self.text_rect.left() - slider_width, top, slider_width, height)

        icon_width = 70
        self.icon_rect = QRect(self.slider_rect.left() - icon_width, top+5, icon_width, height-10)

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(QColor("black")))

        # painter.drawRect(self.text_rect)

        font = QFont()
        font.setFamily("cursive")
        font.setPointSize(14)
        painter.setFont(font)
        volume = 0 if self.mute else round(self.volume*100)
        painter.drawText(QRect(self.text_rect.x()+5, self.text_rect.y()+6, self.text_rect.width()-25,
                               self.text_rect.height()),
                         Qt.AlignHCenter, str(volume))

        h_margin = 4
        v_margin = 2
        # painter.drawRect(self.slider_rect)
        rect = QRect(h_margin+self.slider_rect.left(), int((self.slider_rect.height()/2-v_margin)+self.slider_rect.top()),
                     int(self.slider_rect.width()-h_margin*2), v_margin*2)
        painter.drawRoundedRect(rect, 1, 1)

        radius = 6
        x_pos = rect.left() if self.mute else rect.width() * self.volume + rect.left()
        painter.setBrush(QBrush(painter.pen().color()))
        painter.drawEllipse(QPoint(x_pos, rect.center().y()+1), radius, radius)
        painter.setBrush(QBrush())
        self.precise_slider_rect = QRect(rect.left(), rect.center().y() - radius, rect.width(), radius * 2)

        # painter.drawRect(self.icon_rect)

        painter.setPen(QPen(QColor("black")))
        painter.setBrush(QBrush(QColor("black")))
        len_of_side = math.sqrt(((self.icon_rect.height() * 0.6 / 2) ** 2) / 2)
        len_of_handle = len_of_side / 2
        icon_x = self.icon_rect.width() * 0.6 + self.icon_rect.left()
        painter.drawPolygon(QPolygon([
            QPoint(int(icon_x), int(self.icon_rect.top() + self.icon_rect.height() * 0.8)),  # right top
            QPoint(int(icon_x), int(self.icon_rect.top() + self.icon_rect.height() * 0.2)),  # right bottom
            QPoint(int(icon_x - len_of_side), int(self.icon_rect.top() + self.icon_rect.height() * 0.2 + len_of_side)),
            QPoint(int(icon_x - len_of_side - len_of_handle), int(self.icon_rect.top() + self.icon_rect.height() * 0.2 + len_of_side)),
            # back top
            QPoint(int(icon_x - len_of_side - len_of_handle), int(self.icon_rect.top() + self.icon_rect.height() * 0.8 - len_of_side)),
            # back bottom
            QPoint(int(icon_x - len_of_side), int(self.icon_rect.top() + self.icon_rect.height() * 0.8 - len_of_side))
        ]))
        painter.setBrush(Qt.NoBrush)

        # if self.mute:
        #     font = QFont()
        #     font.setFamily("cursive")
        #     font.setPointSize(11)
        #     painter.setFont(font)
        #     painter.drawText(QRect(int(icon_x+5), int(self.icon_rect.top()+6), 30, 30), 0, "X")

        painter.setPen(QPen(QColor("black")))
        arc1_rect = QRect(int(icon_x-12), (self.icon_rect.top() + 10),
                          20, self.icon_rect.height() - 20)
        painter.drawArc(arc1_rect, 16 * 45, 16 * -90)
        arc2_rect = QRect(int(icon_x - 17), (self.icon_rect.top() + 5),
                          30, self.icon_rect.height() - 10)
        painter.drawArc(arc2_rect, 16 * 45, 16 * -90)
        arc3_rect = QRect(int(icon_x - 22), (self.icon_rect.top()),
                          40, self.icon_rect.height())
        painter.drawArc(arc3_rect, 16 * 45, 16 * -90)

        if self.mute:
            cur_pen = painter.pen()
            pen = QPen(QColor("black"))
            pen.setWidth(2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            # painter.drawRect(QRect(arc3_rect.x(), arc3_rect.y(), arc3_rect.width()+5, arc3_rect.height()))
            painter.drawLine(arc3_rect.x() + 5, arc3_rect.y(), arc3_rect.right(), arc3_rect.bottom())

        painter.end()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            QApplication.exit(0)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.icon_rect.contains(event.pos()):
            self.mute = not self.mute
            self.update()
        elif self.precise_slider_rect.contains(event.pos()):
            self.volume = self.calc_volume_from_pos(event.pos().x())
            self.mouse_down_volume = True
            self.update()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mouse_down_volume:
            self.mouse_down_volume = False

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mouse_down_volume:
            self.volume = self.calc_volume_from_pos(event.pos().x())
            self.update()

    def calc_volume_from_pos(self, x):
        volume = (x - self.precise_slider_rect.left()) / self.precise_slider_rect.width()
        return min(max(0, volume), 1)


# class

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = SliderWindow()
#     ex.show()
#     sys.exit(app.exec_())