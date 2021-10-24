import os

from PyQt5.QtCore import QRect, QEvent, Qt, pyqtSlot
from PyQt5.QtGui import QPainter, QDragEnterEvent, QDropEvent, QKeyEvent, QMouseEvent, QPen, QFont, \
    QFontMetrics, QColor

from goddo_player.VideoPlayer import VideoPlayer
from goddo_player.draw_utils import numpy_to_pixmap
from goddo_player.save_state import State
from goddo_player.time_frame_utils import frames_to_time_components, build_time_str
from goddo_player.ui.play_button import PlayButton
from goddo_player.ui.slider import Slider
from goddo_player.ui.ui_component import UiComponent
from goddo_player.ui.volume_controls import VolumeControl


class FrameInOut:
    def __init__(self):
        self.__in_frame = None
        self.__out_frame = None

    @property
    def in_frame(self):
        return self.__in_frame

    @in_frame.setter
    def in_frame(self, value):
        self.__in_frame = value
        if self.__out_frame and self.__out_frame < self.__in_frame:
            self.__out_frame = None

    @property
    def out_frame(self):
        return self.__out_frame

    @out_frame.setter
    def out_frame(self, value):
        self.__out_frame = value
        if self.__in_frame and self.__in_frame > self.__out_frame:
            self.__in_frame = None


class VideoPreview(UiComponent):
    def __init__(self, parent, get_rect):
        super().__init__(parent, get_rect)

        self.volume_control = VolumeControl(self, self.__get_volume_control_rect)
        self.time_bar_slider = Slider(self, self.__get_time_bar_rect, 0)
        self.time_bar_slider.value_update_slot.connect(self.on_timeline_value_changed)

        self.play_button = PlayButton(self, self.__get_play_btn_rect)

        state = State(os.path.join('..', '..', 'state', 'a.json'), '')
        self.video_player = VideoPlayer(state)
        self.video_player.next_frame_slot.connect(self.update_next_frame)

        self.installEventFilter(self)
        self.is_mouse_over = False

        state.save(self)

        self.is_playing = False

        self.total_time_str = '00:00:00.000'
        self.cur_time_str = '00:00:00.000'

        self.font = self.__get_time_label_font()
        metrics = QFontMetrics(self.font)
        self.width_of_2_chars = metrics.width("00")
        self.width_of_colon = metrics.width(":")
        self.char_height = metrics.capHeight()
        self.width_of_time_label = metrics.width(self.total_time_str)

        self.frame_select_range = FrameInOut()

    @staticmethod
    def __get_time_label_font() -> QFont:
        font = QFont()
        font.setFamily("cursive")
        font.setPointSize(9)
        return font

    @pyqtSlot(float)
    def on_timeline_value_changed(self, value):
        self.__emit_pause_event()
        self.video_player.get_next_frame(int(round(value * self.video_player.total_frames)))
        if not self.time_bar_slider.mouse_down:
            self.__emit_play_event()

    def __get_volume_control_rect(self):
        height = 50
        width = VolumeControl.TEXT_WIDTH + VolumeControl.SLIDER_WIDTH + VolumeControl.ICON_WIDTH
        return QRect(self.get_rect().right() - width, self.get_rect().bottom()-height, width, height)

    def __get_time_bar_rect(self):
        height = 20
        volume_rect = self.volume_control.get_rect()
        return QRect(self.get_rect().left()+1, volume_rect.top() - height, self.get_rect().width()-2, height)

    def __get_play_btn_rect(self):
        height = 50
        return QRect(self.get_rect().left()+5, self.get_rect().bottom() - height, height, height)

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        if event.type() == QEvent.Enter:
            return False
        elif event.type() == QEvent.Leave:
            return False
        elif event.type() == QEvent.DragEnter:
            return False
        elif event.type() == QEvent.Drop:
            return False

        return super().eventFilter(obj, event)

    def mouseEnterEvent(self, event: QEvent) -> None:
        self.is_mouse_over = True
        self.window.update()

    def mouseLeaveEvent(self, event: QEvent) -> None:
        self.is_mouse_over = False
        self.window.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.play_button.get_rect().contains(event.pos()):
            if self.is_playing:
                self.__emit_pause_event()
            else:
                self.__emit_play_event()

    def paint(self, painter: QPainter):
        if self.video_player.cur_frame is not None:
            painter.drawPixmap(self.get_rect(), numpy_to_pixmap(self.video_player.cur_frame))

        if self.is_mouse_over:
            super().paint(painter)

            painter.setFont(self.font)

            orig_pen = painter.pen()
            top = self.time_bar_slider.get_rect().bottom()
            rect = self.play_button.get_rect()
            mid_point = (self.get_rect().bottom() - top) / 2
            x = rect.right() + 10
            y = mid_point + top - 5
            painter.drawText(x, y, f'{self.cur_time_str} /')
            painter.setPen(self.__get_darker_pen(orig_pen))
            painter.drawText(x + self.width_of_2_chars, y + 10 + self.char_height, self.total_time_str)
            painter.setPen(orig_pen)

            if self.frame_select_range.in_frame or self.frame_select_range.out_frame:
                x1 = self.frame_select_range.in_frame / self.video_player.total_frames * (
                    self.get_rect().width()) + self.get_rect().left() if self.frame_select_range.in_frame else self.get_rect().left()
                x2 = self.frame_select_range.out_frame / self.video_player.total_frames * (
                    self.get_rect().width()) + self.get_rect().left() if self.frame_select_range.out_frame else self.get_rect().right()

                rect = QRect(x1, self.time_bar_slider.get_rect().top(), x2 - x1, self.time_bar_slider.get_rect().height())
                painter.fillRect(rect, QColor(166, 166, 166, alpha=150))

    @staticmethod
    def __get_darker_pen(pen):
        darker_pen = QPen(pen)
        darker_pen.setColor(darker_pen.color().darker())
        return darker_pen

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        filename = event.mimeData().text()
        if filename.endswith('.mp4') or filename.endswith('.wmv'):
            event.accept()

    def onDropEvent(self, event: QDropEvent) -> None:
        file_path = event.mimeData().text()
        file_name = file_path[file_path.rindex('/')+1:]

        no_prefix_file_path = file_path[8:] if file_path.startswith('file:///') else file_path
        self.video_player.switch_source(no_prefix_file_path)
        time_components = frames_to_time_components(self.video_player.total_frames, self.video_player.fps)
        self.total_time_str = build_time_str(*time_components)
        self.__emit_play_event()

        self.window.setTitle(file_name)
        self.window.requestActivate()

    @pyqtSlot(object, int)
    def update_next_frame(self, _, frame_no):
        self.cur_time_str = build_time_str(*frames_to_time_components(frame_no, self.video_player.fps))

        self.time_bar_slider.blockSignals(True)
        self.time_bar_slider.pos_pct = frame_no / self.video_player.total_frames
        self.time_bar_slider.blockSignals(False)

        self.window.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Space:
            if self.is_playing:
                self.__emit_pause_event()
            else:
                self.__emit_play_event()
        elif event.key() == Qt.Key_I:
            self.frame_select_range.in_frame = self.video_player.cur_frame_no
        elif event.key() == Qt.Key_O:
            self.frame_select_range.out_frame = self.video_player.cur_frame_no
        else:
            super().keyPressEvent(event)

    def __emit_play_event(self):
        if self.video_player.cap:
            self.is_playing = True
            self.play_button.play_slot.emit()
            self.video_player.play_slot.emit()

    def __emit_pause_event(self):
        if self.video_player.cap:
            self.is_playing = False
            self.play_button.pause_slot.emit()
            self.video_player.pause_slot.emit()
