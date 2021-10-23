import os

from PyQt5.QtCore import QRect, QEvent, Qt, pyqtSlot
from PyQt5.QtGui import QPainter, QDragEnterEvent, QDropEvent, QKeyEvent, QMouseEvent, QPen, QFont, \
    QFontMetrics

from goddo_player.VideoPlayer import VideoPlayer
from goddo_player.draw_utils import numpy_to_pixmap
from goddo_player.save_state import State
from goddo_player.time_frame_utils import frames_to_time_components, build_time_str
from goddo_player.ui.play_button import PlayButton
from goddo_player.ui.slider import Slider
from goddo_player.ui.ui_component import UiComponent
from goddo_player.ui.volume_controls import VolumeControl


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

    @staticmethod
    def __get_time_label_font() -> QFont:
        font = QFont()
        font.setFamily("cursive")
        font.setPointSize(9)
        return font

    @pyqtSlot(float)
    def on_timeline_value_changed(self, value):
        # if self.sender() == self.video_player:
        # print(f'time value changed to {value}')
        # print(f'sender = {self.sender()}')
        print(f'is mouse down {self.time_bar_slider.mouse_down}')
        # self.video_player.
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
            top = self.time_bar_slider.get_rect().bottom()
            rect = self.play_button.get_rect()
            mid_point = (self.get_rect().bottom() - top) / 2
            x = rect.right()+10
            y = mid_point + top - 5
            y2 = mid_point + self.char_height+5 + top
            painter.drawText(x, y, f'{self.cur_time_str} /')
            orig_pen = painter.pen()
            lighter_pen = QPen(painter.pen())
            lighter_pen.setColor(lighter_pen.color().darker(150))
            painter.setPen(lighter_pen)
            painter.drawText(x + self.width_of_2_chars, y2, self.total_time_str)
            painter.setPen(orig_pen)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        # print(f'drag enter {event.mimeData().text()}')
        filename = event.mimeData().text()
        if filename.endswith('.mp4') or filename.endswith('.wmv'):
            event.accept()

    def onDropEvent(self, event: QDropEvent) -> None:
        # print(f'file dropped: {event.mimeData().text()}')
        file_path = event.mimeData().text()
        file_name = file_path[file_path.rindex('/')+1:]

        no_prefix_file_path = file_path[8:] if file_path.startswith('file:///') else file_path
        self.video_player.switch_source(no_prefix_file_path)
        self.total_time_str = build_time_str(*frames_to_time_components(self.video_player.total_frames, self.video_player.fps))
        self.__emit_play_event()

        self.window.setTitle(file_name)
        self.window.requestActivate()

    @pyqtSlot(object, int)
    def update_next_frame(self, frame, frame_no):
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
