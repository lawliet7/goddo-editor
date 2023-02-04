import logging
import math

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QMouseEvent, QBrush
from PyQt5.QtWidgets import QWidget, QToolTip, QMenu, QInputDialog

from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.signals import PlayCommand, SignalFunctionId, StateStoreSignals
from goddo_player.app.state_store import StateStore, VideoClip
from goddo_player.utils.time_frame_utils import frames_to_time_components, build_time_str_least_chars, \
    build_time_ms_str_least_chars
from goddo_player.utils.message_box_utils import show_input_msg_box, show_error_box


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
        file_runtime_details = self.state.file_runtime_details_dict[clip.video_path.str()]

        n_frames = clip.frame_in_out.get_no_of_frames(file_runtime_details.total_frames)
        n_mins = n_frames / file_runtime_details.fps / 60
        width = round(n_mins * self.state.timeline.width_of_one_min)

        return QRect(x, self.height_of_line + 50, width, 100)

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
        if event.buttons() == Qt.LeftButton:
            clip = None
            clip_idx = -1
            for i, t in enumerate(self.clip_rects):
                clip, rect = t
                if rect.contains(event.pos()):
                    logging.info(f'double click {rect} clip at index {i}')

                    clip_idx = i
                    break

            if clip:
                self.signals.preview_window.play_cmd_slot.emit(PlayCommand.PAUSE)
                self.signals.timeline_clip_double_click_slot.emit(clip_idx, clip, SignalFunctionId.no_function())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # super().mousePressEvent(event)

        logging.debug(f'mouse press {event.pos()}')

        if event.buttons() == Qt.LeftButton:
            found_idx = self._get_clip_mouse_clicked_on(event.pos())
            self.signals.timeline_select_clip.emit(found_idx)

    def contextMenuEvent(self, event):
        super().contextMenuEvent(event)

        found_idx = self._get_clip_mouse_clicked_on(event.pos())
        if found_idx > -1:
            logging.info(f'clicked on clip {found_idx}')

            menu = QMenu(self)
            create_clip_action = menu.addAction("create clip")
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == create_clip_action:
                logging.info('creating clip')

                text, ok = show_input_msg_box(self, 'Create Clip', 'clip name: ')
                if ok:
                    if len(text.strip()) > 2:
                        clip = self.state.timeline.clips[found_idx]
                        self.signals.add_clip_slot.emit(text.strip(), clip)
                    else:
                        show_error_box(self, 'Please enter more than 2 characters')

    def _get_clip_mouse_clicked_on(self, pos):
        for i, t in enumerate(self.clip_rects):
            _, rect = t
            if rect.contains(pos):
                logging.info(f'{rect} found clip at index {i}')
                return i
        return -1

    def resize_timeline_widget(self):
        required_total_secs = 0
        for _, c in enumerate(self.state.timeline.clips):
            file_runtime_details = self.state.file_runtime_details_dict[c.video_path.str()]

            final_in_frame = c.frame_in_out.get_resolved_in_frame()
            final_out_frame = c.frame_in_out.get_resolved_out_frame(file_runtime_details.total_frames)
            required_total_secs += (final_out_frame - final_in_frame) / file_runtime_details.fps
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
            painter.drawLine(x, self.height_of_line, x, 393)
            painter.drawText(int(x-size_width/2), self.height_of_line-5, f"{i+1}:00")

            for j in range(6):
                tick_x = int(x - length_of_one_min / 6 * (j+1))
                tick_length = length_of_tick if j == 2 else int(length_of_tick / 2)
                painter.drawLine(tick_x, self.height_of_line, tick_x, int(self.height_of_line + tick_length))

        painter.drawLine(0, self.height_of_line, self.width(), self.height_of_line)

        x = 0
        pen = painter.pen()
        for i, (clip, rect) in enumerate(self.clip_rects):
            file_runtime_details = self.state.file_runtime_details_dict[clip.video_path.str()]

            in_frame = clip.frame_in_out.get_resolved_in_frame()
            out_frame = clip.frame_in_out.get_resolved_out_frame(file_runtime_details.total_frames)

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
            logging.debug(f'=== in_frame={in_frame} out_frame={out_frame} fps={file_runtime_details.fps} total_frames={file_runtime_details.total_frames}')
            in_frame_ts = self.build_time_str(in_frame, file_runtime_details.fps)
            out_frame_ts = self.build_time_str(out_frame, file_runtime_details.fps)
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
                file_runtime_details = self.state.file_runtime_details_dict[c.video_path.str()]
                fps = file_runtime_details.fps
                total_frames = file_runtime_details.total_frames

                filename = c.video_path.file_name()
                in_frame_ts = build_time_str_least_chars(*frames_to_time_components(c.frame_in_out.get_resolved_in_frame(), fps))
                out_frame_ts = build_time_str_least_chars(*frames_to_time_components(c.frame_in_out.get_resolved_out_frame(total_frames), fps))
                frame_diff = c.frame_in_out.get_resolved_out_frame(total_frames) - c.frame_in_out.get_resolved_in_frame()
                duration = build_time_ms_str_least_chars(*frames_to_time_components(frame_diff, fps))
                msg = f'{filename}\n{in_frame_ts} - {out_frame_ts}\nduration: {duration}'
                QToolTip.showText(self.mapToGlobal(event.pos()), msg)
                return

        QToolTip.hideText()
