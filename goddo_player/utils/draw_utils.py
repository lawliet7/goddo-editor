import math
from typing import List, Tuple, Callable

from PyQt5.QtCore import Qt, QPoint, QRect, QLineF, QLine
from PyQt5.QtGui import QImage, QPixmap, QPen, QPainter, QPolygonF, QPaintDevice, QBrush, QColor

from goddo_player.utils.number_utils import convert_to_int


def numpy_to_qimage(numpy):
    height, width, channel = numpy.shape
    bytes_per_line = 3 * width
    return QImage(numpy.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()


def numpy_to_pixmap(numpy):
    return QPixmap(numpy_to_qimage(numpy))


def create_pen(width=1, color=Qt.white):
    pen = QPen()
    pen.setWidth(width)
    pen.setColor(color)
    return pen


def create_fill_in_brush(color: QColor):
    return QBrush(color, Qt.SolidPattern)


def draw_polygon_points(painter: QPainter, points: List[QPoint], brush=None, pen=None):
    polygon = QPolygonF(points)

    if brush:
        painter.setBrush(brush)
    if pen:
        painter.setPen(pen)

    painter.drawPolygon(polygon)


def draw_polygon_tuple(painter: QPainter, points: List[Tuple[int, int]], brush=None, pen=None):
    draw_polygon_points(painter, [QPoint(t[0], t[1]) for t in points], brush=brush, pen=pen)


def paint_helper(paint_device: QPaintDevice, fn: Callable[[QPainter], None], antialias=True):
    painter = QPainter()
    painter.begin(paint_device)

    if antialias:
        painter.setRenderHint(QPainter.Antialiasing)

    pen = painter.pen()
    brush = painter.brush()

    fn(painter)

    painter.setPen(pen)
    painter.setBrush(brush)
    painter.end()


def draw_circle(painter: QPainter, coor: Tuple[int, int], radius: int, pen=None, brush=None):
    if brush:
        painter.setBrush(brush)

    if pen:
        painter.setPen(pen)

    painter.drawEllipse(*coor, radius, radius)


def set_pen_brush_before_paint(painter: QPainter, draw_fn: Callable[[QPainter], None], pen=None, brush=None):
    if pen:
        orig_pen = painter.pen()
        painter.setPen(pen)

    if brush:
        orig_brush = painter.brush()
        painter.setBrush(brush)

    draw_fn(painter)

    if pen:
        painter.setPen(orig_pen)

    if brush:
        painter.setBrush(orig_brush)


def draw_lines(painter: QPainter, lines: List[Tuple[float, float, float, float]], pen=None, brush=None):
    set_pen_brush_before_paint(painter, lambda p: p.drawLines([QLineF(*x) for x in lines]), pen=pen, brush=brush)


def draw_circle(painter: QPainter, rect: QRect, pen=None, brush=None, pct_of_rect=1):
    if brush:
        painter.setBrush(brush)

    if pen:
        painter.setPen(pen)

    radius = convert_to_int(min(rect.height(), rect.width()) * pct_of_rect)
    x = convert_to_int(rect.width() / 2 + rect.x() - radius / 2)
    y = convert_to_int(rect.height() / 2 + rect.y() - radius / 2)
    painter.drawEllipse(x, y, radius, radius)
    return QRect(x, y, radius, radius)


def draw_play_button(painter, rect, is_playing, color=Qt.white, pct_of_rect=0.8):
    # draw circle
    pen = create_pen(width=3, color=color)
    brush = QBrush(color, Qt.NoBrush)
    circle_rect = draw_circle(painter, rect, pen=pen, brush=brush, pct_of_rect=pct_of_rect)

    if is_playing:
        # draw triangle
        center_right_x = convert_to_int(circle_rect.left() + circle_rect.width() * 0.75)
        center_y = convert_to_int(circle_rect.top() + circle_rect.width() / 2)
        triangle_length = circle_rect.width() * 0.5
        base_length = convert_to_int(math.sqrt(triangle_length ** 2 - (triangle_length / 2) ** 2))
        draw_polygon_tuple(painter, [(center_right_x, center_y),
                                     (center_right_x - base_length, convert_to_int(center_y + triangle_length / 2)),
                                     (center_right_x - base_length, convert_to_int(center_y - triangle_length / 2))],
                           brush=QBrush(color, Qt.SolidPattern))
    else:
        # draw 2 bars
        left = convert_to_int(circle_rect.left() + circle_rect.width() * 0.25)
        right = convert_to_int(circle_rect.left() + circle_rect.width() * 0.75)
        top = convert_to_int(circle_rect.top() + circle_rect.width() * 0.25)
        bottom = convert_to_int(circle_rect.top() + circle_rect.width() * 0.75)

        right_of_left_bar = convert_to_int((right - left) * 0.4 + left)
        draw_polygon_tuple(painter, [(left, top), (left, bottom),
                                     (right_of_left_bar, bottom), (right_of_left_bar, top)],
                           brush=QBrush(color, Qt.SolidPattern))

        left_of_right_bar = convert_to_int((right - left) * 0.6 + left)
        draw_polygon_tuple(painter, [(left_of_right_bar, top), (left_of_right_bar, bottom),
                                     (right, bottom), (right, top)],
                           brush=QBrush(color, Qt.SolidPattern))


def draw_slider(rect, painter: QPainter, theme, progress, circle_radius=5):
    painter.setPen(create_pen(color=theme.color.gray))

    y = rect.height() / 2 + rect.top()
    painter.drawLine(rect.left(),  convert_to_int(y),
                     rect.right(),  convert_to_int(y))

    painter.setPen(create_pen(width=3, color=theme.color.controls))
    painter.drawLine(rect.left(), convert_to_int(y),
                     convert_to_int(progress*rect.width()+rect.left()), convert_to_int(y))

    painter.setBrush(QBrush(theme.color.controls, Qt.SolidPattern))
    painter.drawEllipse(convert_to_int(progress*rect.width()+rect.left())-circle_radius,
                        convert_to_int(y)-circle_radius,
                        circle_radius*2, circle_radius*2)
