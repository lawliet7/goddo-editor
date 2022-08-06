import logging
import os
import pathlib
from time import time

import cv2
from PyQt5.QtCore import QObject, QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QLabel

from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.signals import SignalFunctionId, StateStoreSignals, PlayCommand, PositionType
from goddo_player.app.state_store import StateStore, VideoClip
from goddo_player.utils.loading_dialog import LoadingDialog
from goddo_player.utils.video_path import VideoPath
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.preview_window.preview_window import PreviewWindow
from goddo_player.preview_window.preview_window_output import PreviewWindowOutput
from goddo_player.list_window.tabbed_list_window import TabbedListWindow
from goddo_player.timeline_window.timeline_window import TimelineWindow
from goddo_player.utils.enums import IncDec
from goddo_player.utils.message_box_utils import show_error_box
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.window_util import activate_window
from goddo_player.widgets.audio_widget import AudioPlayer2

class MonarchSystem(QObject):
    def __init__(self, app: 'QApplication'):
        super().__init__()

        self.app = app
        self.state = StateStore()

        self.tabbed_list_window = TabbedListWindow()
        self.tabbed_list_window.show()

        left = self.tabbed_list_window.geometry().right()
        top = self.tabbed_list_window.geometry().top() + 20

        self.preview_window = PreviewWindow()
        self.preview_window.show()
        self.preview_window.move(left, top)

        self.preview_window_output = PreviewWindowOutput()
        self.preview_window_output.show()
        self.preview_window_output.move(self.preview_window.geometry().right() + 10, top)

        self.timeline_window = TimelineWindow()
        self.timeline_window.show()
        self.timeline_window.move(left, self.preview_window.geometry().bottom() + 10)

        self.audio_player = AudioPlayer2()

        self.signals: StateStoreSignals = StateStoreSignals()
        self.signals.preview_window.switch_video_slot.connect(self.__on_switch_video)
        self.signals.preview_window_output.switch_video_slot.connect(self.__on_switch_video)
        self.signals.preview_window.update_file_details_slot.connect(self.__on_update_file_details)
        self.signals.preview_window_output.update_file_details_slot.connect(self.__on_update_file_details)
        self.signals.add_file_slot.connect(self.__on_add_file)
        self.signals.add_video_tag_slot.connect(self.__on_add_video_tag)
        self.signals.save_slot.connect(self.__on_save_file)
        self.signals.load_slot.connect(self.__on_load_file)
        self.signals.close_file_slot.connect(self.__on_close_file)
        self.signals.preview_window.in_frame_slot.connect(self.__on_preview_video_in_frame)
        self.signals.preview_window_output.in_frame_slot.connect(self.__on_preview_video_in_frame)
        self.signals.preview_window.out_frame_slot.connect(self.__on_preview_video_out_frame)
        self.signals.preview_window_output.out_frame_slot.connect(self.__on_preview_video_out_frame)
        self.signals.preview_window.play_cmd_slot.connect(self.__on_preview_window_play_cmd)
        self.signals.preview_window_output.play_cmd_slot.connect(self.__on_preview_window_play_cmd)
        self.signals.add_timeline_clip_slot.connect(self.__on_add_timeline_clip)
        self.signals.timeline_select_clip.connect(self.__on_timeline_select_clip)
        self.signals.remove_video_tag_slot.connect(self.__on_remove_video_tag)
        self.signals.preview_window.seek_slot.connect(self.__on_preview_window_seek)
        self.signals.preview_window_output.seek_slot.connect(self.__on_preview_window_seek)
        self.signals.preview_window.switch_speed_slot.connect(self.__on_switch_speed)
        self.signals.preview_window_output.switch_speed_slot.connect(self.__on_switch_speed)
        self.signals.preview_window.update_skip_slot.connect(self.__on_preview_window_update_skip)
        self.signals.preview_window_output.update_skip_slot.connect(self.__on_preview_window_update_skip)
        self.signals.preview_window_output.switch_restrict_frame_slot.connect(self.__on_switch_restrict_frame_slot)
        self.signals.timeline_delete_selected_clip_slot.connect(self.__on_timeline_delete_selected_clip)
        self.signals.timeline_update_width_of_one_min_slot.connect(self.__on_timeline_update_width_of_one_min)
        self.signals.timeline_clip_double_click_slot.connect(self.__on_timeline_clip_double_click)
        self.signals.preview_window.reset_slot.connect(self.__on_preview_window_reset)
        self.signals.preview_window_output.reset_slot.connect(self.__on_preview_window_reset)
        self.signals.timeline_set_clipboard_clip_slot.connect(self.__on_timeline_set_clipboard_clip)
        self.signals.timeline_clear_clipboard_clip_slot.connect(self.__on_timeline_clear_clipboard_clip)
        self.signals.activate_all_windows_slot.connect(self.__on_activate_all_windows)

    def __on_switch_restrict_frame_slot(self):
        self.state.preview_window_output.restrict_frame_interval = not self.state.preview_window_output.restrict_frame_interval
        self.preview_window_output.update()

    def __on_timeline_set_clipboard_clip(self, clip):
        self.state.timeline.clipboard_clip = clip
    
    def __on_timeline_clear_clipboard_clip(self):
        self.state.timeline.clipboard_clip = None

    def __on_timeline_select_clip(self, idx):
        self.state.timeline.selected_clip_index = idx
        self.timeline_window.update()

    def __on_remove_video_tag(self, video_path: VideoPath, tag: str):
        self.state.file_list.files_dict[video_path.str()].delete_tag(tag)
        self.tabbed_list_window.videos_tab.clip_list_dict[video_path.str()].delete_tag(tag)

    def __on_add_video_tag(self, video_path: VideoPath, tag: str):
        self.state.file_list.files_dict[video_path.str()].add_tag(tag)
        self.tabbed_list_window.videos_tab.clip_list_dict[video_path.str()].add_tag(tag)

    def __on_activate_all_windows(self):
        cur_active_window = QApplication.activeWindow()

        if cur_active_window != self.tabbed_list_window:
            activate_window(self.tabbed_list_window)

        if cur_active_window != self.preview_window:
            activate_window(self.preview_window)
        
        if cur_active_window != self.preview_window_output:
            activate_window(self.preview_window_output)
        
        if cur_active_window != self.timeline_window:
            activate_window(self.timeline_window)

        activate_window(cur_active_window)

    def __on_preview_window_reset(self):
        preview_window = self.get_preview_window_from_signal(self.sender())

        def fn():
            self.timeline_window.update()
            preview_window.update()

        fn_id = self.signals.fn_repo.push(fn)
        logging.info(f'=== emitting {fn_id}')
        self.sender().switch_video_slot.emit(VideoPath(QUrl()), FrameInOut(), fn_id)        

    def __on_timeline_clip_double_click(self, idx, clip):
        self.state.timeline.opened_clip_index = idx

        if idx > -1:
            pw_signals = self.signals.preview_window_output
            pw_state = self.state.preview_window_output

            def fn():
                pw_signals.seek_slot.emit(clip.frame_in_out.get_resolved_in_frame(), PositionType.ABSOLUTE)

                if pw_state.is_max_speed:
                    pw_signals.switch_speed_slot.emit()

                pw_signals.play_cmd_slot.emit(PlayCommand.PLAY)
            
            fn_id = self.signals.fn_repo.push(fn)
            logging.info(f'=== emitting {fn_id}')
            pw_signals.switch_video_slot.emit(clip.video_path, clip.frame_in_out, fn_id)
            
        else:
            self.signals.preview_window_output.reset_slot.emit()

    def __on_timeline_update_width_of_one_min(self, inc_dec: IncDec):
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

    def __on_preview_window_update_skip(self, skip_type: IncDec):
        preview_window_state = self.get_preview_window_state_from_signal(self.sender())
        cur_skip = preview_window_state.time_skip_multiplier
        if skip_type is IncDec.INC:
            preview_window_state.time_skip_multiplier = min(cur_skip + 1, 60)
        else:
            preview_window_state.time_skip_multiplier = max(cur_skip - 1, 1)
        self.get_preview_window_from_signal(self.sender()).update()

    def __on_timeline_delete_selected_clip(self):
        selected_idx = self.state.timeline.selected_clip_index
        opened_idx = self.state.timeline.opened_clip_index
        self.state.timeline.clips = [x for i, x in enumerate(self.state.timeline.clips) if i != selected_idx]
        max_idx = len(self.state.timeline.clips)-1
        self.state.timeline.selected_clip_index = min(selected_idx, max_idx)
        self.timeline_window.recalculate_clip_rects()

        if selected_idx == opened_idx:
            self.state.timeline.opened_clip_index = -1
            self.signals.preview_window_output.reset_slot.emit()
        else:
            self.timeline_window.update()
            self.preview_window_output.update()

    def __on_switch_speed(self):
        preview_window = self.get_preview_window_from_signal(self.sender())
        preview_window_state = self.get_preview_window_state_from_signal(self.sender())
        if preview_window.preview_widget.cap is not None:
            is_playing = preview_window.is_playing()
            if is_playing:
                self.sender().play_cmd_slot.emit(PlayCommand.PAUSE)
            speed = preview_window.preview_widget.switch_speed()
            preview_window_state.is_max_speed = (speed == 1)
            preview_window.update()
            if is_playing:
                self.sender().play_cmd_slot.emit(PlayCommand.PLAY)

    def __on_preview_window_seek(self, frame_no: int, pos_type: PositionType):
        preview_window = self.get_preview_window_from_signal(self.sender())
        is_playing = preview_window.is_playing()
        if is_playing:
            self.sender().play_cmd_slot.emit(PlayCommand.PAUSE)
        preview_window.go_to_frame(frame_no, pos_type)
        preview_window_state = self.get_preview_window_state_from_signal(self.sender())

        preview_window_state.current_frame_no = preview_window.preview_widget.get_cur_frame_no()

        if is_playing:
            self.sender().play_cmd_slot.emit(PlayCommand.PLAY)

    def __on_add_timeline_clip(self, clip: VideoClip, idx: int):
        logging.debug(f'monarch on add timeline clip for idx {idx}')

        if idx == -1 or idx == len(self.state.timeline.clips):
            self.state.timeline.clips.append(clip)
        else:
            clips_clone = self.state.timeline.clips[:]
            clips_clone.insert(idx, clip)
            self.state.timeline.clips = clips_clone
        self.timeline_window.recalculate_clip_rects()
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

    def __on_switch_video(self, video_path: VideoPath, frame_in_out: FrameInOut, fn_id: SignalFunctionId):
        logging.info(f'update preview file')
        self.tabbed_list_window.setDisabled(True)
        self.preview_window.preview_widget.setDisabled(True)
        self.preview_window_output.setDisabled(True)
        self.timeline_window.setDisabled(True)

        preview_window = self.get_preview_window_from_signal(self.sender())
        def finished_loading_video():
            self.tabbed_list_window.setDisabled(False)
            self.preview_window.setDisabled(False)
            self.preview_window_output.setDisabled(False)
            self.timeline_window.setDisabled(False)

            preview_window.switch_video(video_path, frame_in_out)
            preview_window.activateWindow()

            logging.info(f'=== fn {fn_id}')
            self.signals.fn_repo.pop(fn_id)()

        self.audio_player.load_audio(str(video_path), os.path.join('output',video_path.file_name(include_ext=False)+'.wav'), finished_loading_video)

    def __on_update_file_details(self, fps: float, total_frames: int):
        preview_window_state = self.get_preview_window_state_from_signal(self.sender())
        preview_window_state.fps = fps
        preview_window_state.total_frames = total_frames
        preview_window_state.current_frame_no = 1 if total_frames > 0 else 0
        preview_window_state.cur_total_frames = preview_window_state.total_frames
        preview_window_state.cur_start_frame = preview_window_state.current_frame_no
        preview_window_state.cur_end_frame = preview_window_state.total_frames

    def __on_add_file(self, video_path: VideoPath):
        if not video_path.str() in self.tabbed_list_window.videos_tab.clip_list_dict:
            cap = cv2.VideoCapture(video_path.str())
            fps = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()

            if fps > 0:
                item = self.state.file_list.create_file_item(video_path)
                self.state.file_list.add_file_item(item)
                self.tabbed_list_window.videos_tab.add_video(video_path)
            elif not os.path.exists(video_path.str()):
                show_error_box(self.tabbed_list_window.videos_tab,
                            f"file not found! - {video_path.str()}")
            else:
                show_error_box(self.tabbed_list_window.videos_tab,
                            f"your system doesn't support file format dropped! - {video_path.str()}")
        else:
            show_error_box(self.tabbed_list_window.videos_tab, 'video already exists!', title='Duplicate Video')

    def __on_save_file(self, video_path: VideoPath):
        self.signals.preview_window.play_cmd_slot.emit(PlayCommand.PAUSE)
        self.state.save_file(video_path)

    def __on_close_file(self):
        # load empty file so it resets the state
        self.signals.load_slot.emit(VideoPath(QUrl()))

        self.tabbed_list_window.videos_tab.list_widget.clear()
        self.tabbed_list_window.videos_tab.clip_list_dict.clear()
        self.tabbed_list_window.clips_tab.list_widget.clear()
        self.tabbed_list_window.clips_tab.clip_list_dict.clear()
        self.signals.preview_window.play_cmd_slot.emit(PlayCommand.PAUSE)
        self.signals.preview_window_output.play_cmd_slot.emit(PlayCommand.PAUSE)
        logging.info(f'=== emitting {0}')
        logging.info(f'=== emitting {0}')
        self.signals.preview_window.switch_video_slot.emit(VideoPath(QUrl()), FrameInOut(), SignalFunctionId.no_function)
        self.signals.preview_window_output.switch_video_slot.emit(VideoPath(QUrl()), FrameInOut(), SignalFunctionId.no_function)

        self.timeline_window.recalculate_clip_rects()
        # self.timeline_window.activateWindow()
        self.timeline_window.update()

    def __on_load_file(self, video_path: VideoPath):
        def handle_file_fn(file_dict):
            signals = StateStoreSignals()

            my_url = file_to_url(file_dict['name'])
            my_video_path = VideoPath(my_url)
            signals.add_file_slot.emit(my_video_path)

            for tag in file_dict['tags']:
                signals.add_video_tag_slot.emit(my_video_path, tag)

        def handle_prev_wind_fn(prev_wind_dict):
            pw_signals = StateStoreSignals().preview_window

            def fn():
                logging.debug(f"loading in out {prev_wind_dict['frame_in_out']}")

                if prev_wind_dict['current_frame_no'] > 0:
                    pw_signals.seek_slot.emit(prev_wind_dict['current_frame_no'], PositionType.ABSOLUTE)
                else:
                    pw_signals.seek_slot.emit(0, PositionType.ABSOLUTE)

                if prev_wind_dict.get('is_max_speed'):
                    pw_signals.switch_speed_slot.emit()

                if prev_wind_dict.get('time_skip_multiplier'):
                    new_multiplier = prev_wind_dict['time_skip_multiplier']
                    cur_multiplier = self.state.preview_window.time_skip_multiplier

                    if new_multiplier > cur_multiplier:
                        for i in range(new_multiplier - cur_multiplier):
                            pw_signals.update_skip_slot.emit(IncDec.INC)
                    elif new_multiplier < cur_multiplier:
                        for i in range(cur_multiplier - new_multiplier):
                            pw_signals.update_skip_slot.emit(IncDec.DEC)                    

            frame_in_out_dict = prev_wind_dict['frame_in_out']
            frame_in_out = FrameInOut(frame_in_out_dict.get('in_frame'), frame_in_out_dict.get('out_frame'))
            fn_id = self.signals.fn_repo.push(fn)
            logging.info(f'=== emitting {fn_id}')
            pw_signals.switch_video_slot.emit(VideoPath(file_to_url(prev_wind_dict['video_path'])), frame_in_out, fn_id)
            

        def handle_prev_wind_output_fn(prev_wind_out_dict):
            pw_signals = StateStoreSignals().preview_window_output

            if self.state.timeline.opened_clip_index > -1:

                if not prev_wind_out_dict['restrict_frame_interval']:
                    pw_signals.switch_restrict_frame_slot.emit()

                if prev_wind_out_dict['current_frame_no'] > 0:
                    pw_signals.seek_slot.emit(prev_wind_out_dict['current_frame_no'], PositionType.ABSOLUTE)
                else:
                    pw_signals.seek_slot.emit(0, PositionType.ABSOLUTE)

                if prev_wind_out_dict.get('is_max_speed'):
                    pw_signals.switch_speed_slot.emit()

                if prev_wind_out_dict.get('time_skip_multiplier'):
                    new_multiplier = prev_wind_out_dict['time_skip_multiplier']
                    cur_multiplier = self.state.preview_window.time_skip_multiplier

                    if new_multiplier > cur_multiplier:
                        for i in range(new_multiplier - cur_multiplier):
                            pw_signals.update_skip_slot.emit(IncDec.INC)
                    elif new_multiplier < cur_multiplier:
                        for i in range(cur_multiplier - new_multiplier):
                            pw_signals.update_skip_slot.emit(IncDec.DEC)

                # if prev_wind_out_dict.get('time_skip_multiplier'):


        def handle_timeline_fn(timeline_dict):
            for clip_dict in timeline_dict['clips']:
                StateStoreSignals().add_timeline_clip_slot.emit(VideoClip.from_dict(clip_dict), -1)

            if timeline_dict.get('width_of_one_min'):
                width_of_one_min = timeline_dict['width_of_one_min']
                if width_of_one_min > PlayerConfigs.timeline_initial_width_of_one_min:
                    iterations = int((width_of_one_min - PlayerConfigs.timeline_initial_width_of_one_min) / 6)
                    for _ in range(iterations):
                        StateStoreSignals().timeline_update_width_of_one_min_slot.emit(IncDec.INC)
                elif width_of_one_min < PlayerConfigs.timeline_initial_width_of_one_min:
                    iterations = int((PlayerConfigs.timeline_initial_width_of_one_min - width_of_one_min) / 6)
                    for _ in range(iterations):
                        StateStoreSignals().timeline_update_width_of_one_min_slot.emit(IncDec.DEC)
            
            if timeline_dict.get('selected_clip_index') > -1:
                StateStoreSignals().timeline_select_clip.emit(timeline_dict.get('selected_clip_index'))

            if timeline_dict.get('clipboard_clip'):
                StateStoreSignals().timeline_set_clipboard_clip_slot.emit(VideoClip.from_dict(timeline_dict.get('clipboard_clip')))

            if timeline_dict.get('opened_clip_index') > -1:
                idx = timeline_dict.get('opened_clip_index')
                opened_clip = VideoClip.from_dict(timeline_dict['clips'][idx])
                self.signals.timeline_clip_double_click_slot.emit(idx, opened_clip)
                self.signals.preview_window_output.play_cmd_slot.emit(PlayCommand.PAUSE)

        self.state.load_file(video_path, handle_file_fn, handle_prev_wind_fn, handle_prev_wind_output_fn, handle_timeline_fn)

    def __on_preview_video_in_frame(self, pos: int):
        logging.info(f'update in frame to {pos} sender={self.sender()}')

        preview_window_state = self.get_preview_window_state_from_signal(self.sender())
        if pos != -1 and not (0 <= pos <= preview_window_state.total_frames):
            raise RuntimeError(f"Going to invalid in position: {pos}, total_frames={preview_window_state.total_frames}")

        new_pos = pos if pos >= 0 else None
        preview_window_state.frame_in_out = preview_window_state.frame_in_out.update_in_frame(new_pos)

        if self.sender() is self.signals.preview_window_output:
            opened_clip = self.state.timeline.clips[self.state.timeline.opened_clip_index]
            timeline_in_frame = opened_clip.frame_in_out.get_resolved_in_frame()

            if timeline_in_frame != new_pos:
                clip = self.state.timeline.clips[self.state.timeline.opened_clip_index]
                new_clip = VideoClip(video_path=clip.video_path, fps=clip.fps, total_frames=clip.total_frames,
                                        frame_in_out=preview_window_state.frame_in_out)
                self.state.timeline.clips[self.state.timeline.opened_clip_index] = new_clip
                self.timeline_window.inner_widget.recalculate_all_clip_rects()
                self.timeline_window.update()

                self._update_preview_window_output_cur_frames(preview_window_state, new_clip)

    def __on_preview_video_out_frame(self, pos: int):
        logging.info(f'update out frame to {pos}')

        preview_window_state = self.get_preview_window_state_from_signal(self.sender())
        if pos != -1 and not (0 <= pos <= preview_window_state.total_frames):
            raise RuntimeError(f"Going to invalid out position: {pos}, total_frames={preview_window_state.total_frames}")

        new_pos = pos if pos >= 0 else None
        preview_window_state.frame_in_out = preview_window_state.frame_in_out.update_out_frame(new_pos)

        if self.sender() is self.signals.preview_window_output:
            clip = self.state.timeline.clips[self.state.timeline.opened_clip_index]
            timeline_out_frame = clip.frame_in_out.get_resolved_out_frame(clip.total_frames)

            if timeline_out_frame != new_pos:
                new_clip = VideoClip(video_path=clip.video_path, fps=clip.fps, total_frames=clip.total_frames,
                                        frame_in_out=preview_window_state.frame_in_out)
                self.state.timeline.clips[self.state.timeline.opened_clip_index] = new_clip
                self.timeline_window.inner_widget.recalculate_all_clip_rects()
                self.timeline_window.update()

                self._update_preview_window_output_cur_frames(preview_window_state, new_clip)

    def _update_preview_window_output_cur_frames(self, preview_window_state, clip):
        resolved_in_frame = clip.frame_in_out.get_resolved_in_frame()
        resolved_out_frame = clip.frame_in_out.get_resolved_out_frame(preview_window_state.total_frames)

        extra_frames_in_secs_config = self.state.app_config.extra_frames_in_secs_config
        extra_frames_config = int(round(extra_frames_in_secs_config * preview_window_state.fps))
        in_frame_in_secs = int(round(resolved_in_frame / preview_window_state.fps)) if preview_window_state.fps > 0 else 0
        leftover_frames = preview_window_state.total_frames - resolved_out_frame
        leftover_frames_in_secs = int(round(leftover_frames / preview_window_state.fps))
        extra_frames_on_left = extra_frames_config if in_frame_in_secs > extra_frames_in_secs_config else resolved_in_frame - 1
        extra_frames_on_right = extra_frames_config if leftover_frames_in_secs > extra_frames_in_secs_config else leftover_frames

        preview_window_state.cur_start_frame = preview_window_state.frame_in_out.get_resolved_in_frame() - extra_frames_on_left
        preview_window_state.cur_end_frame = preview_window_state.frame_in_out.get_resolved_out_frame(preview_window_state.total_frames) + extra_frames_on_right
        preview_window_state.cur_total_frames = preview_window_state.cur_end_frame - preview_window_state.cur_start_frame + 1
        self.preview_window_output.update()

    def __on_preview_window_play_cmd(self, play_cmd: PlayCommand):
        preview_window = self.get_preview_window_from_signal(self.sender())
        before_toggle_is_playing = preview_window.preview_widget.is_playing()

        preview_window_state = self.get_preview_window_state_from_signal(self.sender())

        preview_window.toggle_play_pause(play_cmd)

        if play_cmd == PlayCommand.PAUSE or before_toggle_is_playing:
            preview_window_state.current_frame_no = preview_window.preview_widget.get_cur_frame_no()
