import logging
import math

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QMouseEvent, QBrush
from PyQt5.QtWidgets import QWidget, QToolTip

from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.signals import StateStoreSignals
from goddo_player.app.state_store import StateStore, VideoClip
from goddo_player.utils.time_frame_utils import frames_to_time_components, build_time_str_least_chars, \
    build_time_ms_str_least_chars


class TimelineWidget(QWidget):
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
        self.height_of_line = 1

        self.clip_rects = []

        self.setMouseTracking(True)

    def calc_rect_for_clip(self, clip: VideoClip, x=0):
        n_frames = clip.frame_in_out.get_no_of_frames(clip.total_frames)
        n_mins = n_frames / clip.fps / 60
        width = round(n_mins * self.state.timeline.width_of_one_min)

        return QRect(x, self.height_of_line + 50, width, self.height())

    def recalculate_all_clip_rects(self):
        x = 0
        new_clip_rects = []
        for clip in self.state.timeline.clips:
            rect = self.calc_rect_for_clip(clip, x)
            new_clip_rects.append((clip, rect))
            x += rect.width()

        self.clip_rects = new_clip_rects
        self.resize_timeline_widget()

    def initPainter(self, painter: QtGui.QPainter) -> None:
        super().initPainter(painter)

        self.height_of_line = painter.fontMetrics().height() + 5

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        for i, t in enumerate(self.clip_rects):
            clip, rect = t
            if rect.contains(event.pos()):
                logging.info(f'double click {rect} clip at index {i}')

                self.signals.timeline_clip_double_click_slot.emit(i, clip)

                return

        self.signals.timeline_clip_double_click_slot.emit(-1, clip)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # super().mousePressEvent(event)

        logging.debug(f'mouse press {event.pos()}')

        for i, t in enumerate(self.clip_rects):
            _, rect = t
            if rect.contains(event.pos()):
                logging.info(f'{rect} found clip at index {i}')
                self.signals.timeline_select_clip.emit(i)
                return

        self.signals.timeline_select_clip.emit(-1)

    def resize_timeline_widget(self):
        required_total_secs = 0
        for _, c in enumerate(self.state.timeline.clips):
            final_in_frame = c.frame_in_out.get_resolved_in_frame()
            final_out_frame = c.frame_in_out.get_resolved_out_frame(c.total_frames)
            required_total_secs += (final_out_frame - final_in_frame) / c.fps
        cur_total_secs = self.width() / self.state.timeline.width_of_one_min * 60
        logging.debug(f'required_total_secs={required_total_secs} cur_total_secs={cur_total_secs}')
        if required_total_secs + 60 > cur_total_secs or required_total_secs + 60 < cur_total_secs:
            x = int(round((required_total_secs / 60 + 1) * self.state.timeline.width_of_one_min))
            x = max(x, PlayerConfigs.timeline_initial_width)
            self.resize(x, self.height())

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size_width = painter.fontMetrics().width('00:00')

        length_of_one_min = self.state.timeline.width_of_one_min
        length_of_tick = length_of_one_min / 6

        # height_of_line = painter.fontMetrics().height()+5
        painter.setPen(QColor(173, 202, 235))
        for i in range(int(math.ceil(self.width() / length_of_one_min))):
            x = (i+1) * length_of_one_min
            painter.drawLine(x, self.height_of_line, x, self.height())
            painter.drawText(int(x-size_width/2), self.height_of_line-5, f"{i+1}:00")

            for j in range(6):
                tick_x = int(x - length_of_one_min / 6 * (j+1))
                tick_length = length_of_tick if j == 2 else int(length_of_tick / 2)
                painter.drawLine(tick_x, self.height_of_line, tick_x, int(self.height_of_line + tick_length))

        painter.drawLine(0, self.height_of_line, self.width(), self.height_of_line)

        x = 0
        pen = painter.pen()
        for i, (clip, rect) in enumerate(self.clip_rects):
            in_frame = clip.frame_in_out.get_resolved_in_frame()
            out_frame = clip.frame_in_out.get_resolved_out_frame(clip.total_frames)

            painter.fillRect(rect, Qt.darkRed)
            pen = painter.pen()
            painter.setPen(Qt.red)
            painter.drawRect(rect)

            if self.state.timeline.opened_clip_index == i:
                color = Qt.lightGray
                orig_brush = painter.brush()
                painter.setPen(color)
                painter.setBrush(QBrush(color, Qt.SolidPattern))
                if rect.width() >= PlayerConfigs.timeline_length_of_triangle:
                    top_left_pt = QPoint(rect.right() - PlayerConfigs.timeline_length_of_triangle, rect.top())
                    bott_right_pt = QPoint(rect.right(), rect.top() + PlayerConfigs.timeline_length_of_triangle)
                else:
                    top_left_pt = QPoint(rect.left(), rect.top())
                    bott_right_pt = QPoint(rect.right(), rect.top() + rect.width())
                painter.drawPolygon(top_left_pt, rect.topRight(), bott_right_pt)
                painter.setBrush(orig_brush)

            painter.setPen(Qt.white)
            filename = clip.video_path.file_name()
            logging.debug(f'=== in_frame={in_frame} out_frame={out_frame} fps={clip.fps} total_frames={clip.total_frames}')
            in_frame_ts = self.build_time_str(in_frame, clip.fps)
            out_frame_ts = self.build_time_str(out_frame, clip.fps)
            painter.drawText(rect, Qt.TextWordWrap, f'{filename}\n{in_frame_ts} - {out_frame_ts}')
            x += rect.width()

        if self.state.timeline.selected_clip_index >= 0:
            painter.setPen(Qt.green)
            painter.drawRect(self.clip_rects[self.state.timeline.selected_clip_index][1])

        painter.setPen(pen)
        painter.end()

    @staticmethod
    def build_time_str(no_of_frames, fps):
        return build_time_str_least_chars(*frames_to_time_components(no_of_frames, fps))

    def mouseMoveEvent(self, event):
        for c, rect in self.clip_rects:
            if rect.contains(event.pos()):
                filename = c.video_path.file_name()
                in_frame_ts = build_time_str_least_chars(*frames_to_time_components(c.frame_in_out.get_resolved_in_frame(), c.fps))
                out_frame_ts = build_time_str_least_chars(*frames_to_time_components(c.frame_in_out.get_resolved_out_frame(c.total_frames), c.fps))
                frame_diff = c.frame_in_out.get_resolved_out_frame(c.total_frames) - c.frame_in_out.get_resolved_in_frame()
                duration = build_time_ms_str_least_chars(*frames_to_time_components(frame_diff, c.fps))
                msg = f'{filename}\n{in_frame_ts} - {out_frame_ts}\nduration: {duration}'
                QToolTip.showText(self.mapToGlobal(event.pos()), msg)
                return

        QToolTip.hideText()
