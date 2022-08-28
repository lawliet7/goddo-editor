from goddo_player.list_window.tabbed_list_window import TabbedListWindow
from goddo_player.preview_window.preview_window import PreviewWindow
from goddo_player.preview_window.preview_window_output import PreviewWindowOutput
from goddo_player.timeline_window.timeline_window import TimelineWindow
from goddo_player.widgets.audio_widget import AudioPlayer
from goddo_test.utils.test_utils import qrect_as_dict, qsize_as_dict


class WindowsContainer:
    def __init__(self, tabbed_list_window: TabbedListWindow, preview_window: PreviewWindow, output_window: PreviewWindowOutput, timeline_window: TimelineWindow) -> None:
        self.tabbed_list_window = tabbed_list_window
        self.preview_window = preview_window
        self.output_window = output_window
        self.timeline_window = timeline_window

    def _get_audio_player_dict(self, audio_player: AudioPlayer):
        if audio_player.worker: 
            return {
                'audio_path': audio_player.worker.audio_wave._file.file.name,
                'frame_rate': audio_player.worker.audio_wave.getframerate(),
                'channels': audio_player.worker.audio_wave.getnchannels(),
                'no_of_frames': audio_player.worker.audio_wave.getnframes(),
                'sample_width': audio_player.worker.audio_wave.getsampwidth(),
                'cur_pos': audio_player.worker.audio_wave.tell(),
            }
        else:
            return {

            }

    def as_dict(self):
        return {
          'tabbed_list_window': {
              'isEnabled': self.tabbed_list_window.isEnabled(),
              'windowTitle': self.tabbed_list_window.windowTitle(),
              'geometry': qrect_as_dict(self.tabbed_list_window.geometry()),
              # not sure if we should also include screenshot pixmap
              'videos_tab': {
                'clips': self._get_clip_dict(self.tabbed_list_window.videos_tab.list_widget)
              },
              'clips_tab': {
                'clips': self._get_clip_dict(self.tabbed_list_window.clips_tab.list_widget)
              }
          },
          'preview_window': {
              'isEnabled': self.preview_window.isEnabled(),
              'windowTitle': self.preview_window.windowTitle(),
              'geometry': qrect_as_dict(self.preview_window.geometry()),
              'label': self.preview_window.label.text(),
              'slider': {
                  'value': self.preview_window.slider.value(),
                  'isEnabled': self.preview_window.slider.isEnabled()
              },
              'audioPlayer': self._get_audio_player_dict(self.preview_window.preview_widget.audio_player)
          },
          'output_window': {
              'isEnabled': self.output_window.isEnabled(),
              'windowTitle': self.output_window.windowTitle(),
              'geometry': qrect_as_dict(self.output_window.geometry()),
              'label': self.output_window.label.text(),
              'slider': {
                  'value': self.output_window.slider.value(),
                  'isEnabled': self.output_window.slider.isEnabled()
              },
              'audioPlayer': self._get_audio_player_dict(self.preview_window.preview_widget.audio_player)
          },
          'timeline_window': {
              'isEnabled': self.timeline_window.isEnabled(),
              'windowTitle': self.timeline_window.windowTitle(),
              'geometry': qrect_as_dict(self.timeline_window.geometry()),
              'innerWidgetSize': qsize_as_dict(self.timeline_window.inner_widget.size()),
              'clip_rects': [(c.as_dict(),qrect_as_dict(r)) for c,r in self.timeline_window.inner_widget.clip_rects]
          }
        }

    @staticmethod
    def _get_clip_dict(list_widget):
        clips = []
        for item in list_widget.get_all_items():
            item_widget = list_widget.itemWidget(item)

            tags = []
            for i in range(item_widget.flow_layout.count()):
                tags.append(item_widget.flow_layout.itemAt(i).text())
            
            clip_dict = {
                'name': item_widget.file_name_label.text(),
                'tags': tags
            }
            clips.append(clip_dict)
        return clips

