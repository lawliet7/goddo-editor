import pickle

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QVBoxLayout

from goddo_player.DragAndDrop import VideoClipDragItem
from goddo_player.draw_utils import *
from goddo_player.time_frame_utils import *
from goddo_player.window_util import *


class TimelineWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, get_geometry_fn, state):
        super().__init__()
        self.get_parent_geometry = get_geometry_fn
        self.state = state

        # print(parent_window.geometry())

        y = self.get_parent_geometry().bottom() + get_title_bar_height() + 10
        x = 10

        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()

        self.setGeometry(x, y, screen_rect.width()-20, screen_rect.bottom() - y - 10)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.scrolling = False
        self.scrollbar_rect: QRect = None
        self.scrollbar_prev_pos: QPoint = None
        self.scrollbar_width = 40
        self.scrollbar_height = 15
        self.scrollbar_min_x = 2
        self.scrollbar_speed = 10
        self.scrollbar_max_x = self.geometry().width() - self.scrollbar_min_x - self.scrollbar_width

        self.grid_offset = 0
        self.scrollbar_x_offset = 0
        # self.state.timeline['clips'] = []

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        data = pickle.loads(event.mimeData().data("custom"))
        print(data)

        self.state.timeline.clips.append(data)
        self.update()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Left:
            self.scrollbar_x_offset = self.scrollbar_x_offset - 1
            print(f"left {self.scrollbar_x_offset}")
            self.update()
        elif event.key() == Qt.Key_Right:
            self.scrollbar_x_offset = self.scrollbar_x_offset + 1
            print(f"right {self.scrollbar_x_offset}")
            self.update()
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            print("save it")
            self.state.save(self)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_P:
            import subprocess
            import os

            tmp_dir = 'tmp'
            for f in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, f))

            for i, x in enumerate(self.state.timeline.clips):
                start_time = x.in_frame * x.video['fps'] / 1000
                end_time = x.out_frame * x.video['fps'] / 1000
                cmd = f"ffmpeg -ss {start_time} -i {x.video['video_path']} -to {end_time - start_time} -cbr 15 -metadata title=\"you suck\" tmp/{i:04}.mp4"
                print(f'executing cmd: {cmd}')
                subprocess.call(cmd, shell=True)

            # concat_data = '\n'.join([f'file {os.path.join(tmp_dir, f)}' for f in os.listdir(tmp_dir)])
            tmp_vid_files = [f"file '{os.path.join(tmp_dir, f)}'\n" for f in os.listdir(tmp_dir)]
            with open(os.path.join(tmp_dir, 'concat.txt'), mode='w', encoding='utf-8') as f:
                f.writelines(tmp_vid_files)

            cmd = f"ffmpeg -f concat -safe 0 -i tmp\concat.txt -c copy output\output_{time.time()}.mp4"
            print(f'executing cmd: {cmd}')
            subprocess.call(cmd, shell=True)

            print('output generated!!')


        else:
            super().keyPressEvent(event)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        brush = create_fill_in_brush(QColor(51, 51, 51))
        rect = QtCore.QRect(0, 0, painter.device().width(), painter
                            .device().height())
        painter.fillRect(rect, brush)

        regular_pen = create_pen(width=0.1, color=Qt.white)
        half_opacity_pen = create_pen(width=0.1, color=QColor(255,255,255,100))
        painter.setPen(regular_pen)

        height = 30
        painter.drawLine(0, height, self.geometry().width(), height)

        tick_time_in_secs = 6
        tick_spacing = 10
        tick_height = 10

        i = 0
        x = 0
        while x < self.geometry().width():
            offset = self.scrollbar_x_offset*self.scrollbar_speed*-1
            x = i*tick_spacing+offset
            if x >= 0:
                if i % 10 == 0:
                    cur_tick_height = height - tick_height * 1.5
                elif i % 5 == 0:
                    cur_tick_height = height - tick_height
                else:
                    cur_tick_height = height - tick_height / 2
                painter.setPen(regular_pen)
                painter.drawLine(x, height, x, cur_tick_height)

                if i % 10 == 0:
                    painter.setPen(half_opacity_pen)
                    painter.drawLine(x, height, x, self.geometry().height())

                    painter.setPen(regular_pen)
                    time_str = format_time(*ms_to_time_components(1000*60*i/10, 30))
                    painter.drawText(QPoint(x, 10), time_str)

            i = i + 1

        painter.setPen(regular_pen)
        painter.drawRect(QRect(0, self.geometry().height()-self.scrollbar_height,
                               self.geometry().width(), self.scrollbar_height))

        x = min(self.scrollbar_max_x, max(self.scrollbar_min_x, self.scrollbar_min_x+self.scrollbar_x_offset))
        self.scrollbar_rect = QRect(x, self.geometry().height() - self.scrollbar_height+4,
                                    self.scrollbar_width, self.scrollbar_height-8)
        painter.setBrush(create_fill_in_brush(Qt.white))
        painter.drawRoundedRect(self.scrollbar_rect, 3, 3)

        midpoint = (height + self.scrollbar_rect.y()) / 2

        # print(self.videos)

        # print(self.state.timeline['clips'])
        x = -self.scrollbar_x_offset*self.scrollbar_speed
        for v in self.state.timeline.clips:

            width = v.total_secs / tick_time_in_secs * tick_spacing

            if width+x >= 0:
                color = QColor(0, 179, 60)
                border_color = QColor(0, 77, 26)
                painter.setPen(border_color)
                painter.setBrush(QBrush(color))
                box_height = 50
                video_rect = QRect(x, midpoint-box_height, width, box_height)
                painter.drawRect(video_rect)

                video_text = f"{v.video['video_path']}\n{format_time(*frames_to_time_components(v.total_frames, v.fps))}"
                painter.setPen(Qt.black)
                painter.drawText(video_rect.adjusted(2, 2, -2, -2), Qt.TextWordWrap, video_text)

            x = x + width

        print(self.geometry())

    def mousePressEvent(self, event: QMouseEvent):
        print("mouse press")
        if self.scrollbar_rect.contains(event.pos()):
            self.scrolling = True
            self.scrollbar_prev_pos = event.pos()
        # self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        print("mouse release")
        self.scrolling = False

    def mouseMoveEvent(self, event: QMouseEvent):
        print("mouse move")
        if self.scrolling:
            print(event.pos())
            # self.grid_offset = self.grid_offset - (event.pos().x() - self.scrollbar_prev_pos.x())
            self.update()

    def enterEvent(self, event: QtCore.QEvent):
        self.activateWindow()



