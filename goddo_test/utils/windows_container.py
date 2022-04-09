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

