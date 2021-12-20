import logging
import math

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QPainter, QColor, QMouseEvent
from PyQt5.QtWidgets import QWidget, QToolTip

from goddo_player.signals import StateStoreSignals
from goddo_player.state_store import StateStore, TimelineClip
from goddo_player.time_frame_utils import frames_to_time_components, build_time_str_least_chars, \
    build_time_ms_str_least_chars


class TimelineWidget(QWidget):
    INITIAL_WIDTH = 1075
    WIDTH_OF_ONE_MIN = 120
    LENGTH_OF_TICK = 20

    def __init__(self):
        super().__init__()
        # self.get_height = get_height
        # self.scroll_area = scroll_area

        # self.setWindowTitle('臥底女捜査官')
        # self.setWindowTitle('美少女捜査官')
        # self.setGeometry(600, 550, 1024, 360)

        self.state = StateStore()
        self.signals = StateStoreSignals()

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(12, 29, 45))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.clip_rects = []
        self.selected_clip_index = -1

        self.setMouseTracking(True)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # super().mousePressEvent(event)

        logging.debug(f'mouse press {event.pos()}')

        for i, t in enumerate(self.clip_rects):
            _, rect = t
            if rect.contains(event.pos()):
                logging.info(f'{rect} found clip at index {i}')
                self.selected_clip_index = i
                self.update()
                return

        self.selected_clip_index = -1
        self.update()

    def resize_timeline_widget(self):
        required_total_secs = 0
        for i, c in enumerate(self.state.timeline.clips):
            final_in_frame = c.frame_in_out.in_frame if c.frame_in_out.in_frame is not None else 1
            final_out_frame = c.frame_in_out.out_frame if c.frame_in_out.out_frame is not None else c.total_frames
            required_total_secs += (final_out_frame - final_in_frame) / c.fps
        cur_total_secs = self.width() / self.WIDTH_OF_ONE_MIN * 60
        logging.info(f'required_total_secs={required_total_secs} cur_total_secs={cur_total_secs}')
        if required_total_secs + 60 > cur_total_secs:
            x = (required_total_secs / 60 + 1) * self.WIDTH_OF_ONE_MIN
            self.resize(x, self.height())
        elif required_total_secs + 60 < cur_total_secs:
            self.resize(self.INITIAL_WIDTH, self.height())

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        logging.info('painting')
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size_width = painter.fontMetrics().width('00:00')

        height_of_line = painter.fontMetrics().height()+5
        painter.setPen(QColor(173, 202, 235))
        for i in range(int(math.ceil(self.width()/self.WIDTH_OF_ONE_MIN))):
            x = (i+1)*self.WIDTH_OF_ONE_MIN
            painter.drawLine(x, height_of_line, x, 393)
            painter.drawText(int(x-size_width/2), height_of_line-5, f"{i+1}:00")

            for j in range(6):
                tick_x = int(x - self.WIDTH_OF_ONE_MIN/6*(j+1))
                tick_length = self.LENGTH_OF_TICK if j == 2 else int(self.LENGTH_OF_TICK / 2)
                painter.drawLine(tick_x, height_of_line, tick_x, height_of_line + tick_length)

        painter.drawLine(0, height_of_line, self.width(), height_of_line)

        x = 0
        for i, c in enumerate(self.state.timeline.clips):
            in_frame = c.frame_in_out.in_frame
            out_frame = c.frame_in_out.out_frame
            if out_frame and in_frame:
                n_frames = out_frame - in_frame
            elif in_frame:
                n_frames = c.total_frames - in_frame
            elif out_frame:
                n_frames = out_frame
            else:
                raise Exception("both in and out frame is blank")
            n_mins = n_frames / c.fps / 60
            width = n_mins * self.WIDTH_OF_ONE_MIN
            rect = QRect(x, height_of_line+50, width, 100)
            painter.fillRect(rect, Qt.darkRed)
            pen = painter.pen()
            if i == self.selected_clip_index:
                painter.setPen(Qt.green)
            else:
                painter.setPen(Qt.red)
            painter.drawRect(rect)

            final_in_frame = in_frame if in_frame is not None else 1
            final_out_frame = out_frame if out_frame is not None else c.total_frames

            painter.setPen(Qt.white)
            filename = c.video_url.fileName()
            in_frame_ts = build_time_str_least_chars(*frames_to_time_components(final_in_frame, c.fps))
            out_frame_ts = build_time_str_least_chars(*frames_to_time_components(final_out_frame, c.fps))
            painter.drawText(rect, Qt.TextWordWrap, f'{filename}\n{in_frame_ts} - {out_frame_ts}')
            painter.setPen(pen)
            x += width + 1

        painter.end()

    def mouseMoveEvent(self, event):
        for i, t in enumerate(self.clip_rects):
            c, rect = t
            if rect.contains(event.pos()):
                filename = c.video_url.fileName()
                in_frame_ts = build_time_str_least_chars(*frames_to_time_components(c.frame_in_out.in_frame, c.fps))
                out_frame_ts = build_time_str_least_chars(*frames_to_time_components(c.frame_in_out.out_frame, c.fps))
                frame_diff = c.frame_in_out.out_frame - c.frame_in_out.in_frame
                duration = build_time_ms_str_least_chars(*frames_to_time_components(frame_diff, c.fps))
                msg = f'{filename}\n{in_frame_ts} - {out_frame_ts}\nduration: {duration}'
                QToolTip.showText(self.mapToGlobal(event.pos()), msg)
                return

        QToolTip.hideText()

    def add_rect_for_new_clip(self, clip: TimelineClip):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        height_of_line = painter.fontMetrics().height() + 5

        x = 0
        for c, rect in self.clip_rects:
            x += rect.width()

        in_frame = clip.frame_in_out.in_frame
        out_frame = clip.frame_in_out.out_frame
        if out_frame and in_frame:
            n_frames = out_frame - in_frame
        elif in_frame:
            n_frames = clip.total_frames - in_frame
        elif out_frame:
            n_frames = out_frame
        else:
            raise Exception("both in and out frame is blank")
        n_mins = n_frames / clip.fps / 60
        width = n_mins * self.WIDTH_OF_ONE_MIN
        rect = QRect(x, height_of_line + 50, width, 100)
        self.clip_rects.append((clip, rect))

        painter.end()
