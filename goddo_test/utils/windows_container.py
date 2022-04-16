from goddo_player.list_window.clip_list_window import ClipItemWidget
from goddo_player.list_window.tabbed_list_window import TabbedListWindow
from goddo_player.preview_window.preview_window import PreviewWindow
from goddo_player.preview_window.preview_window_output import PreviewWindowOutput
from goddo_player.timeline_window.timeline_window import TimelineWindow


class WindowsContainer:
    def __init__(self, tabbed_list_window: TabbedListWindow, preview_window: PreviewWindow, output_window: PreviewWindowOutput, timeline_window: TimelineWindow) -> None:
        self.tabbed_list_window = tabbed_list_window
        self.preview_window = preview_window
        self.output_window = output_window
        self.timeline_window = timeline_window

    def as_dict(self):
        vid_list_widget = self.tabbed_list_window.videos_tab.listWidget
        for item in vid_list_widget.get_all_items():
            item_widget: ClipItemWidget = vid_list_widget.itemWidget(item)
            x = {

            }


        return {
          'tabbed_list_window': {
              'windowTitle': self.tabbed_list_window.windowTitle(),
              'videos_tab': {

              },
              'clips_tab': {

              }
          },
          'preview_window': {
              'windowTitle': self.preview_window.windowTitle()
          },
          'output_window': {
              'windowTitle': self.output_window.windowTitle()
          },
          'timeline_window': {
              'windowTitle': self.timeline_window.windowTitle()
          }
        }

