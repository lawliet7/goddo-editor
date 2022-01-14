import logging

from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtWidgets import QApplication

from goddo_player.enums import IncDec
from goddo_player.file_list import FileList
from goddo_player.frame_in_out import FrameInOut
from goddo_player.player_configs import PlayerConfigs
from goddo_player.preview_window import PreviewWindow
from goddo_player.signals import StateStoreSignals, PlayCommand, PositionType
from goddo_player.state_store import StateStore, TimelineClip
from goddo_player.timeline_window import TimelineWindow
from goddo_player.ui.preview_window_output import PreviewWindowOutput


class MonarchSystem(QObject):
    def __init__(self, app: 'QApplication'):
        super().__init__()

        self.app = app
        self.state = StateStore()

        self.file_list = FileList()
        self.file_list.show()

        left = self.file_list.geometry().left() + 50
        top = self.file_list.geometry().top() + 20

        self.preview_window = PreviewWindow()
        self.preview_window.show()
        self.preview_window.move(left, top)

        self.preview_window_output = PreviewWindowOutput()
        self.preview_window_output.show()
        self.preview_window_output.move(self.preview_window.geometry().right() + 10, top)

        self.timeline_window = TimelineWindow()
        self.timeline_window.show()
        self.timeline_window.move(left, self.preview_window.geometry().bottom() + 10)

        self.signals: StateStoreSignals = StateStoreSignals()
        self.signals.preview_window.switch_video_slot.connect(self.__on_update_preview_file)
        self.signals.preview_window_output.switch_video_slot.connect(self.__on_update_preview_file)
        self.signals.preview_window.update_file_details_slot.connect(self.__on_update_preview_file_details)
        self.signals.preview_window_output.update_file_details_slot.connect(self.__on_update_preview_file_details)
        self.signals.add_file_slot.connect(self.__on_add_file)
        self.signals.save_slot.connect(self.__on_save_file)
        self.signals.load_slot.connect(self.__on_load_file)
        self.signals.preview_window.in_frame_slot.connect(self.__on_preview_video_in_frame_slot)
        self.signals.preview_window_output.in_frame_slot.connect(self.__on_preview_video_in_frame_slot)
        self.signals.preview_window.out_frame_slot.connect(self.__on_preview_video_out_frame_slot)
        self.signals.preview_window_output.out_frame_slot.connect(self.__on_preview_video_out_frame_slot)
        self.signals.preview_window.play_cmd_slot.connect(self.__on_preview_window_play_cmd_slot)
        self.signals.preview_window_output.play_cmd_slot.connect(self.__on_preview_window_play_cmd_slot)
        self.signals.add_timeline_clip_slot.connect(self.__on_add_timeline_clip_slot)
        self.signals.preview_window.seek_slot.connect(self.__on_preview_window_seek_slot)
        self.signals.preview_window_output.seek_slot.connect(self.__on_preview_window_seek_slot)
        self.signals.preview_window.switch_speed_slot.connect(self.__on_switch_speed_slot)
        self.signals.preview_window_output.switch_speed_slot.connect(self.__on_switch_speed_slot)
        self.signals.preview_window.update_skip_slot.connect(self.__on_preview_window_update_skip_slot)
        self.signals.preview_window_output.update_skip_slot.connect(self.__on_preview_window_update_skip_slot)
        self.signals.timeline_delete_selected_clip_slot.connect(self.__on_timeline_delete_selected_clip_slot)
        self.signals.timeline_update_width_of_one_min_slot.connect(self.__on_timeline_update_width_of_one_min_slot)
        self.signals.timeline_clip_double_click_slot.connect(self.__on_timeline_clip_double_click_slot)
        self.signals.preview_window.reset_slot.connect(self.__on_preview_window_reset_slot)
        self.signals.preview_window_output.reset_slot.connect(self.__on_preview_window_reset_slot)

    def __on_preview_window_reset_slot(self):
        preview_window = self.get_preview_window_from_signal(self.sender())
        

    def __on_timeline_clip_double_click_slot(self, idx, clip, _):
        self.state.timeline.opened_clip_index = idx

        pw_signals = self.signals.preview_window_output
        pw_state = self.state.preview_window_output

        pw_signals.switch_video_slot.emit(clip.video_url, False)

        if clip.frame_in_out.in_frame is not None:
            pw_signals.in_frame_slot.emit(clip.frame_in_out.in_frame)

        if clip.frame_in_out.out_frame is not None:
            pw_signals.out_frame_slot.emit(clip.frame_in_out.out_frame)

        extra_frames_in_secs_config = pw_state.extra_frames_in_secs_config
        extra_frames_config = int(round(pw_state.extra_frames_in_secs_config * pw_state.fps))
        in_frame = pw_state.frame_in_out.get_resolved_in_frame()
        in_frame_in_secs = int(round(in_frame / pw_state.fps))
        leftover_frames = pw_state.total_frames - pw_state.frame_in_out.get_resolved_out_frame(pw_state.total_frames)
        leftover_frames_in_secs = int(round(leftover_frames / pw_state.fps))
        extra_frames_on_left = extra_frames_config \
            if in_frame_in_secs > extra_frames_in_secs_config \
            else in_frame
        extra_frames_on_right = extra_frames_config \
            if leftover_frames_in_secs > extra_frames_in_secs_config \
            else leftover_frames
        total_extra_frames = extra_frames_on_left + extra_frames_on_right
        start_frame = pw_state.frame_in_out.get_resolved_in_frame() - extra_frames_on_left
        no_of_frames = int(round(pw_state.frame_in_out.calc_no_of_frames(pw_state.total_frames) + total_extra_frames))
        no_of_ticks = int(round(no_of_frames / pw_state.fps * 4))  # 4 ticks per sec of video
        self.preview_window_output.slider.setRange(0, no_of_ticks)

        pw_state.no_of_frames = no_of_frames
        pw_state.start_frame = start_frame
        pw_state.extra_frames_on_left = extra_frames_on_left
        pw_state.extra_frames_on_right = extra_frames_on_right
        logging.debug(f'no_of_frames={no_of_frames} no_of_ticks={no_of_ticks} '
                      f'max={self.preview_window_output.slider.maximum()}')
        logging.debug(pw_state)

        pw_signals.seek_slot.emit(clip.frame_in_out.get_resolved_in_frame(), PositionType.ABSOLUTE)

        if pw_state.is_max_speed:
            pw_signals.switch_speed_slot.emit()

        pw_signals.play_cmd_slot.emit(PlayCommand.PLAY)

    def __on_timeline_update_width_of_one_min_slot(self, inc_dec: IncDec):
        if inc_dec is IncDec.INC:
            self.state.timeline.width_of_one_min = min(self.state.timeline.width_of_one_min + 6,
                                                       PlayerConfigs.timeline_max_width_of_one_min)
        else:
            self.state.timeline.width_of_one_min = max(self.state.timeline.width_of_one_min - 6,
                                                       PlayerConfigs.timeline_min_width_of_one_min)
        logging.debug(f'width_of_one_min updated to {self.state.timeline.width_of_one_min}')

        logging.debug(f'before clip rects {self.timeline_window.inner_widget.clip_rects}')

        self.timeline_window.recalculate_clip_rects()

        logging.debug(f'after clip rects {self.timeline_window.inner_widget.clip_rects}')

        self.timeline_window.update()

    def __on_preview_window_update_skip_slot(self, skip_type: IncDec):
        preview_window_state = self.get_preview_window_state_from_signal(self.sender())
        cur_skip = preview_window_state.time_skip_multiplier
        if skip_type is IncDec.INC:
            preview_window_state.time_skip_multiplier = min(cur_skip + 1, 60)
        else:
            preview_window_state.time_skip_multiplier = max(cur_skip - 1, 1)
        self.get_preview_window_from_signal(self.sender()).update()

    def __on_timeline_delete_selected_clip_slot(self):
        selected_idx = self.state.timeline.selected_clip_index
        opened_idx = self.state.timeline.opened_clip_index
        self.state.timeline.clips = [x for i, x in enumerate(self.state.timeline.clips) if i != selected_idx]
        max_idx = len(self.state.timeline.clips)-1
        self.state.timeline.selected_clip_index = min(selected_idx, max_idx)
        self.timeline_window.recalculate_clip_rects()

        if selected_idx == opened_idx:
            self.state.timeline.opened_clip_index = -1
            self.signals.preview_window_output.switch_video_slot.emit(QUrl(), False)

        self.timeline_window.update()
        self.preview_window_output.update()

    def __on_switch_speed_slot(self):
        preview_window = self.get_preview_window_from_signal(self.sender())
        preview_window_state = self.get_preview_window_state_from_signal(self.sender())
        is_playing = preview_window.is_playing()
        if is_playing:
            self.sender().play_cmd_slot.emit(PlayCommand.PAUSE)
        speed = preview_window.preview_widget.switch_speed()
        preview_window_state.is_max_speed = (speed == 1)
        preview_window.update()
        if is_playing:
            self.sender().play_cmd_slot.emit(PlayCommand.PLAY)

    def __on_preview_window_seek_slot(self, frame_no: int, pos_type: PositionType):
        preview_window = self.get_preview_window_from_signal(self.sender())
        is_playing = preview_window.is_playing()
        if is_playing:
            self.sender().play_cmd_slot.emit(PlayCommand.PAUSE)
        preview_window.go_to_frame(frame_no, pos_type)
        if is_playing:
            self.sender().play_cmd_slot.emit(PlayCommand.PLAY)

    def __on_add_timeline_clip_slot(self, clip: TimelineClip):
        logging.info('monarch on add timeline clip')
        self.state.timeline.clips.append(clip)
        self.timeline_window.add_rect_for_new_clip(clip)
        self.timeline_window.activateWindow()
        self.timeline_window.update()

    def get_preview_window_from_signal(self, signal):
        if signal is self.signals.preview_window:
            return self.preview_window
        elif signal is self.signals.preview_window_output:
            return self.preview_window_output
        else:
            return None

    def get_preview_window_state_from_signal(self, signal):
        if signal is self.signals.preview_window:
            return self.state.preview_window
        elif signal is self.signals.preview_window_output:
            return self.state.preview_window_output
        else:
            return None

    def __on_update_preview_file(self, url: 'QUrl', should_play: bool):
        logging.info(f'update preview file')
        preview_window = self.get_preview_window_from_signal(self.sender())
        preview_window_state = self.get_preview_window_state_from_signal(self.sender())

        preview_window_state.video_url = url
        preview_window_state.frame_in_out = FrameInOut()
        preview_window.switch_video(preview_window_state.video_url)
        if should_play:
            self.sender().play_cmd_slot.emit(PlayCommand.PLAY)
        preview_window.activateWindow()

    def __on_update_preview_file_details(self, fps: float, total_frames: int):
        preview_window_state = self.get_preview_window_state_from_signal(self.sender())
        preview_window_state.fps = fps
        preview_window_state.total_frames = total_frames

    def __on_add_file(self, url: 'QUrl'):
        item = self.state.file_list.create_file_item(url)
        self.state.file_list.add_file_item(item)
        self.file_list.add_video(item.name)

    def __on_save_file(self, url: QUrl):
        self.signals.preview_window.play_cmd_slot.emit(PlayCommand.PAUSE)
        self.state.preview_window.current_frame_no = self.preview_window.preview_widget.get_cur_frame_no()
        self.state.save_file(url)

    def __on_load_file(self, url: QUrl):
        def handle_file_fn(file_dict):
            StateStoreSignals().add_file_slot.emit(QUrl.fromLocalFile(file_dict['name']))

        def handle_prev_wind_fn(prev_wind_dict):
            pw_signals = StateStoreSignals().preview_window

            pw_signals.switch_video_slot.emit(QUrl.fromLocalFile(prev_wind_dict['video_url']), False)
            logging.debug(f"loading in out {prev_wind_dict['frame_in_out']}")

            frame_in_out_dict = prev_wind_dict['frame_in_out']

            if 'in_frame' in frame_in_out_dict:
                pw_signals.in_frame_slot.emit(frame_in_out_dict['in_frame'])

            if 'out_frame' in frame_in_out_dict:
                pw_signals.out_frame_slot.emit(frame_in_out_dict['out_frame'])

            if prev_wind_dict['current_frame_no'] > 1:
                pw_signals.seek_slot.emit(prev_wind_dict['current_frame_no'], PositionType.ABSOLUTE)
            else:
                pw_signals.seek_slot.emit(0, PositionType.ABSOLUTE)

            if 'is_max_speed' in prev_wind_dict:
                pw_signals.switch_speed_slot.emit()

            if 'time_skip_multiplier' in prev_wind_dict:
                new_multiplier = prev_wind_dict['time_skip_multiplier']
                cur_multiplier = self.state.preview_window.time_skip_multiplier

                if new_multiplier > cur_multiplier:
                    for i in range(new_multiplier - cur_multiplier):
                        pw_signals.update_skip_slot.emit(IncDec.INC)
                elif new_multiplier < cur_multiplier:
                    for i in range(cur_multiplier - new_multiplier):
                        pw_signals.update_skip_slot.emit(IncDec.DEC)

        def handle_timeline_fn(timeline_dict):
            for clip_dict in timeline_dict['clips']:
                StateStoreSignals().add_timeline_clip_slot.emit(TimelineClip.from_dict(clip_dict))

            if 'width_of_one_min' in timeline_dict:
                width_of_one_min = timeline_dict['width_of_one_min']
                if width_of_one_min > PlayerConfigs.timeline_initial_width:
                    iterations = int((width_of_one_min - PlayerConfigs.timeline_initial_width) / 6)
                    for i in range(iterations):
                        StateStoreSignals().timeline_update_width_of_one_min_slot.emit(IncDec.DEC)
                elif width_of_one_min < PlayerConfigs.timeline_initial_width:
                    iterations = int((PlayerConfigs.timeline_initial_width - width_of_one_min) / 6)
                    for i in range(iterations):
                        StateStoreSignals().timeline_update_width_of_one_min_slot.emit(IncDec.INC)

        self.state.load_file(url, handle_file_fn, handle_prev_wind_fn, handle_timeline_fn)

    def __on_preview_video_in_frame_slot(self, pos: int):
        logging.info(f'update in frame to {pos} sender={self.sender()}')
        preview_window_state = self.get_preview_window_state_from_signal(self.sender())
        preview_window_state.frame_in_out = preview_window_state.frame_in_out.update_in_frame(pos)

        if self.sender() is self.signals.preview_window_output:
            opened_clip = self.state.timeline.clips[self.state.timeline.opened_clip_index]
            timeline_in_frame = opened_clip.frame_in_out.get_resolved_in_frame()

            if timeline_in_frame != pos:
                clip = self.state.timeline.clips[self.state.timeline.opened_clip_index]
                new_clip = TimelineClip(video_url=clip.video_url, fps=clip.fps, total_frames=clip.total_frames,
                                        frame_in_out=preview_window_state.frame_in_out)
                self.state.timeline.clips[self.state.timeline.opened_clip_index] = new_clip
                self.timeline_window.inner_widget.recalculate_all_clip_rects()
                self.timeline_window.update()

    def __on_preview_video_out_frame_slot(self, pos: int):
        logging.info(f'update out frame to {pos}')
        preview_window_state = self.get_preview_window_state_from_signal(self.sender())
        preview_window_state.frame_in_out = preview_window_state.frame_in_out.update_out_frame(pos)

        if self.sender() is self.signals.preview_window_output:
            clip = self.state.timeline.clips[self.state.timeline.opened_clip_index]
            timeline_out_frame = clip.frame_in_out.get_resolved_out_frame(clip.total_frames)

            if timeline_out_frame != pos:
                new_clip = TimelineClip(video_url=clip.video_url, fps=clip.fps, total_frames=clip.total_frames,
                                        frame_in_out=preview_window_state.frame_in_out)
                self.state.timeline.clips[self.state.timeline.opened_clip_index] = new_clip
                self.timeline_window.inner_widget.recalculate_all_clip_rects()
                self.timeline_window.update()

    def __on_preview_window_play_cmd_slot(self, play_cmd: PlayCommand):
        self.get_preview_window_from_signal(self.sender()).toggle_play_pause(play_cmd)
