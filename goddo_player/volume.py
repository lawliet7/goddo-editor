import math
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QRect, Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPolygon
from PyQt5.QtWidgets import QWidget, QApplication


class VolumeControl(QWidget):
    def __init__(self, state,
                 get_geometry_fn, update_volume_callback_fn, update_ui_fn,
                 color: QColor = QColor('black')):
        super().__init__()

        self.state = state
        # self.setGeometry(10, 60, 1024, 768)
        # self.setWindowTitle('Icon')

        self.get_geometry = get_geometry_fn
        self.update_volume_callback = update_volume_callback_fn
        self.update_ui = update_ui_fn
        self.color = color

        self.text_rect: QRect = None
        self.slider_rect: QRect = None
        self.precise_slider_rect: QRect = None
        self.icon_rect: QRect = None
        self.mouse_down_volume = False

        # print(f'volume: {self.get_geometry()}')
        self.update()

    def paint(self, painter: QPainter) -> None:
        # print("paint")

        height = 50
        top = self.get_geometry().height() - height
        # self.rect = QRect(0, top, self.geometry().width(), height)

        text_width = 70
        self.text_rect = QRect(self.get_geometry().width() - text_width, top, text_width, height)

        slider_width = 100
        self.slider_rect = QRect(self.text_rect.left() - slider_width, top, slider_width, height)

        icon_width = 70
        self.icon_rect = QRect(self.slider_rect.left() - icon_width, top+5, icon_width, height-10)

        orig_pen = painter.pen()
        orig_brush = painter.brush()
        orig_font = painter.font()
        # painter = QPainter()
        # painter.begin(self)
        # painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(self.color))

        # painter.drawRect(self.text_rect)

        font = QFont()
        font.setFamily("cursive")
        font.setPointSize(14)
        painter.setFont(font)
        volume = 0 if self.state.source['is_muted'] else round(self.state.source['volume']*100)
        painter.drawText(QRect(self.text_rect.x()+5, self.text_rect.center().y()-11, self.text_rect.width()-25,
                               self.text_rect.height()),
                         Qt.AlignHCenter, str(volume))

        h_margin = 4
        v_margin = 2
        # painter.drawRect(self.slider_rect)
        rect = QRect(h_margin+self.slider_rect.left(), int((self.slider_rect.height()/2-v_margin)+self.slider_rect.top()),
                     int(self.slider_rect.width()-h_margin*2), v_margin*2)
        painter.drawRoundedRect(rect, 1, 1)

        radius = 6
        x_pos = rect.left() if self.state.source['is_muted'] else rect.width() * self.state.source['volume'] + rect.left()
        painter.setBrush(QBrush(painter.pen().color()))
        painter.drawEllipse(QPoint(x_pos, rect.center().y()+1), radius, radius)
        painter.setBrush(QBrush())
        self.precise_slider_rect = QRect(rect.left(), rect.center().y() - radius, rect.width(), radius * 2)

        # painter.drawRect(self.icon_rect)

        painter.setPen(QPen(self.color))
        painter.setBrush(QBrush(self.color))
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

        painter.setPen(QPen(self.color))
        arc1_rect = QRect(int(icon_x-12), (self.icon_rect.top() + 10),
                          20, self.icon_rect.height() - 20)
        painter.drawArc(arc1_rect, 16 * 45, 16 * -90)
        arc2_rect = QRect(int(icon_x - 17), (self.icon_rect.top() + 5),
                          30, self.icon_rect.height() - 10)
        painter.drawArc(arc2_rect, 16 * 45, 16 * -90)
        arc3_rect = QRect(int(icon_x - 22), (self.icon_rect.top()),
                          40, self.icon_rect.height())
        painter.drawArc(arc3_rect, 16 * 45, 16 * -90)

        if self.state.source['is_muted']:
            # cur_pen = painter.pen()
            pen = QPen(self.color)
            pen.setWidth(2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            # painter.drawRect(QRect(arc3_rect.x(), arc3_rect.y(), arc3_rect.width()+5, arc3_rect.height()))
            painter.drawLine(arc3_rect.x() + 5, arc3_rect.y(), arc3_rect.right(), arc3_rect.bottom())

        # painter.end()

        painter.setPen(orig_pen)
        painter.setBrush(orig_brush)
        painter.setFont(orig_font)

    # def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
    #     if event.key() == Qt.Key_Escape:
    #         QApplication.exit(0)
    #     else:
    #         super().keyPressEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        # print('mouse presss in volume')
        if self.icon_rect.contains(event.pos()):
            self.state.source['is_muted'] = not self.state.source['is_muted']
            self.update_ui()
            self.update_volume_callback(0 if self.state.source['is_muted'] else self.state.source['volume'])
        elif self.precise_slider_rect.contains(event.pos()):
            self.state.source['volume'] = self.calc_volume_from_pos(event.pos().x())
            self.mouse_down_volume = True
            self.update_ui()
            self.update_volume_callback(self.state.source['volume'])
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        # print('mouse release in volume')

        if self.mouse_down_volume:
            self.mouse_down_volume = False

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # print('mouse move in volume')
        if self.mouse_down_volume:
            self.state.source['volume'] = self.calc_volume_from_pos(event.pos().x())
            self.update_ui()
            self.update_volume_callback(self.state.source['volume'])

    def calc_volume_from_pos(self, x):
        volume = (x - self.precise_slider_rect.left()) / self.precise_slider_rect.width()
        return min(max(0, volume), 1)


# class

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = SliderWindow()
#     ex.show()
#     sys.exit(app.exec_())
