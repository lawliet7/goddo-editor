import logging
import re
import time

import pyautogui
import pytest
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QLabel
from goddo_player.utils.time_frame_utils import time_str_to_frames

from goddo_player.utils.video_path import VideoPath
from goddo_player.preview_window.frame_in_out import FrameInOut
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.window_util import get_center_pos_of_widget, local_to_global_pos
from goddo_test.common_asserts import assert_state_is_blank
from goddo_test.utils.assert_utils import *
from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.path_util import video_folder_path, my_test_output_folder_path
from goddo_test.utils.test_utils import *
from goddo_test.utils.windows_container import WindowsContainer


def test_drop_clip_in_only(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(in_frame=in_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame))

def test_drop_clip_in_only_hover(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    hover_over_rect_and_assert(windows_container.timeline_window)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(in_frame=in_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame))

def test_drop_clip_out_only(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    click_on_prev_wind_slider(windows_container.preview_window, 0.95)

    pyautogui.press('o')

    out_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(slider_range=(0.93,0.97),out_frame=out_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(out_frame=out_frame))

def test_drop_clip_out_only_hover(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    click_on_prev_wind_slider(windows_container.preview_window, 0.95)

    pyautogui.press('o')

    out_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    hover_over_rect_and_assert(windows_container.timeline_window)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(slider_range=(0.93,0.97),out_frame=out_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(out_frame=out_frame))            

def test_drop_clip_in_out(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    click_on_prev_wind_slider(windows_container.preview_window, 0.95)

    pyautogui.press('o')

    out_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(slider_range=(0.93,0.97), in_frame=in_frame, out_frame=out_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame, out_frame=out_frame))

def test_drop_clip_in_out_hover(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    click_on_prev_wind_slider(windows_container.preview_window, 0.95)

    pyautogui.press('o')

    out_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    hover_over_rect_and_assert(windows_container.timeline_window)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False),
            get_assert_preview_for_test_file_1_fn(slider_range=(0.93,0.97), in_frame=in_frame, out_frame=out_frame),
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame, out_frame=out_frame))            

def test_zoom_in_on_timeline(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    for _ in range(3):
        pyautogui.press('add')

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(in_frame=in_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame, width_of_one_min=138))

def test_zoom_out_on_timeline(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_test_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    pyautogui.press('i')

    in_frame = app_thread.mon.state.preview_window.current_frame_no

    drop_cur_to_timeline(windows_container)

    for _ in range(3):
        pyautogui.press('subtract')

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_test_file_1_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_test_file_1_fn(in_frame=in_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True), 
            get_assert_timeline_for_test_file_1_fn(in_frame=in_frame, width_of_one_min=102))

def test_timeline_width_expand(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_blank_1hr_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:10:00.00')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)

    drop_cur_to_timeline(windows_container)

    expected_out_frame = 4 * 60 * 10

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_1hr_file_fn(slider_range=(0.15,0.19), current_frame_no=expected_out_frame, out_frame=expected_out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_1hr_file_fn(out_frame=expected_out_frame, clip_rect_widths=[1200], scroll_area_width=1320))

def test_timeline_double_width_expand(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_blank_1hr_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:10:00.00')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)

    drop_cur_to_timeline(windows_container)
    drop_cur_to_timeline(windows_container)

    expected_out_frame = 4 * 60 * 10

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_1hr_file_fn(slider_range=(0.15,0.19), current_frame_no=expected_out_frame, out_frame=expected_out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_1hr_file_fn(out_frame=expected_out_frame, num_of_clips=2, clip_rect_widths=[1200, 1200], scroll_area_width=2519))

def test_delete_clip_and_retract_width(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_blank_1hr_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:05:00.00')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)

    drop_cur_to_timeline(windows_container)
    drop_cur_to_timeline(windows_container)
    wait_until(lambda: windows_container.timeline_window.inner_widget.width() == 1319)

    timeline_window = windows_container.timeline_window
    pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    pyautogui.moveTo(pt.x() + 600 + 10, pt.y() + 68 + 10)
    pyautogui.click()
    pyautogui.press('delete')
    wait_until(lambda: len(windows_container.timeline_window.inner_widget.clip_rects) == 1)

    expected_out_frame = 4 * 60 * 5

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_1hr_file_fn(slider_range=(0.08,0.09), current_frame_no=expected_out_frame, out_frame=expected_out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_1hr_file_fn(out_frame=expected_out_frame, clip_rect_widths=[600], selected_clip_index=0))

def test_delete_clip_after_double_width_expand(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_blank_1hr_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:10:00.00')

    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)

    drop_cur_to_timeline(windows_container)
    drop_cur_to_timeline(windows_container)
    wait_until(lambda: windows_container.timeline_window.inner_widget.width() == 2519)

    timeline_window = windows_container.timeline_window
    pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    pyautogui.moveTo(pt.x() + 600 + 10, pt.y() + 68 + 10)
    pyautogui.click()
    pyautogui.press('delete')
    wait_until(lambda: len(windows_container.timeline_window.inner_widget.clip_rects) == 1)

    expected_out_frame = 4 * 60 * 10

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_1hr_file_fn(slider_range=(0.15,0.19), current_frame_no=expected_out_frame, out_frame=expected_out_frame), 
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_for_1hr_file_fn(out_frame=expected_out_frame, clip_rect_widths=[1200], selected_clip_index=0, scroll_area_width=1320))

def test_retract_by_changing_clip_size_after_double_width_expand(app_thread, windows_container: WindowsContainer, blank_state):
    video_path = get_blank_1hr_vid_path()
    drop_video_on_preview(app_thread, windows_container, video_path)

    enter_time_in_go_to_dialog_box(app_thread, '0:10:00.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)

    drop_cur_to_timeline(windows_container)
    drop_cur_to_timeline(windows_container)
    wait_until(lambda: windows_container.timeline_window.inner_widget.width() == 2519)

    timeline_window = windows_container.timeline_window
    pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    pyautogui.doubleClick(pt.x() + 600 + 10, pt.y() + 68 + 10)
    wait_until(lambda: windows_container.output_window.preview_widget.cap is not None)

    press_space_to_pause(windows_container.output_window)

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')
    pyautogui.press('o')
    wait_until(lambda: windows_container.timeline_window.inner_widget.width() == 1439)

    expected_out_frame1 = 4 * 60
    expected_out_frame2 = 4 * 600

    clip1 = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame1)
    clip2 = get_video_clip_for_1hr_vid(in_frame=None, out_frame=expected_out_frame2)
    expected_timeline_clips = [(clip1,120),(clip2,1200)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_for_1hr_fn(), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_1hr_file_fn(slider_range=(0.15,0.19), current_frame_no=expected_out_frame2, out_frame=expected_out_frame2), 
            get_assert_preview_fn(clip1, slider_range=(0.85, 0.86), is_output_window=True, extra_frames_left=0, extra_frames_right=40),
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, opened_clip_index=0, scroll_area_width=1439))

def test_drop_clips_from_diff_videos(app_thread, windows_container: WindowsContainer, blank_state):
    video_path1 = get_blank_15m_vid_path()
    video_path2 = get_blank_1hr_vid_path()
    drop_video_on_file_list(app_thread, windows_container, [video_path1, video_path2])

    video_tab_list_widget = app_thread.mon.tabbed_list_window.videos_tab.list_widget
    item = video_tab_list_widget.get_all_items()[0]
    item_widget = video_tab_list_widget.itemWidget(item)
    pt = local_to_global_pos(item_widget, video_tab_list_widget)
    pyautogui.moveTo(pt.x() + 10, pt.y() + 10)
    pyautogui.doubleClick()
    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)
    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    enter_time_in_go_to_dialog_box(app_thread, '0:03:00.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)
    drop_cur_to_timeline(windows_container)

    video_tab_list_widget = app_thread.mon.tabbed_list_window.videos_tab.list_widget
    item = video_tab_list_widget.get_all_items()[1]
    item_widget = video_tab_list_widget.itemWidget(item)
    pt = local_to_global_pos(item_widget, video_tab_list_widget)
    pyautogui.moveTo(pt.x() + 10, pt.y() + 10)
    pyautogui.doubleClick()
    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)
    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    enter_time_in_go_to_dialog_box(app_thread, '0:04:00.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)
    drop_cur_to_timeline(windows_container)

    expected_out_frame1 = 3 * 60 * 24
    timeline_clip1 = get_video_clip_for_15m_vid(out_frame=expected_out_frame1)

    expected_out_frame2 = 4 * 60 * 4
    timeline_clip2 = get_video_clip_for_1hr_vid(out_frame=expected_out_frame2)

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_fn([(video_path1, []),(video_path2, [])]), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_1hr_file_fn(slider_range=(0.05,0.07), current_frame_no=expected_out_frame2, out_frame=expected_out_frame2), 
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_fn([(timeline_clip1,360),(timeline_clip2,480)]))

def test_cut_and_paste_clips(app_thread, windows_container: WindowsContainer, blank_state):
    preview_window = windows_container.preview_window
    pw_pt_x, pw_pt_y = get_center_pos_of_widget(preview_window.preview_widget, preview_window)

    video_path = get_blank_1hr_vid_path()
    drop_video_on_file_list(app_thread, windows_container, [video_path])

    video_tab_list_widget = app_thread.mon.tabbed_list_window.videos_tab.list_widget
    item = video_tab_list_widget.get_all_items()[0]
    item_widget = video_tab_list_widget.itemWidget(item)
    pt = local_to_global_pos(item_widget, video_tab_list_widget)
    pyautogui.doubleClick(x=pt.x() + 10, y=pt.y() + 10)
    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)
    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)
    drop_cur_to_timeline(windows_container)
    
    pyautogui.click(x=pw_pt_x + 10, y=pw_pt_y + 10)

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)
    enter_time_in_go_to_dialog_box(app_thread, '0:02:00.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)
    drop_cur_to_timeline(windows_container)

    pyautogui.click(x=pw_pt_x + 10, y=pw_pt_y + 10)

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)
    enter_time_in_go_to_dialog_box(app_thread, '0:03:00.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)
    drop_cur_to_timeline(windows_container)

    timeline_window = windows_container.timeline_window
    pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    pyautogui.click(x=pt.x() + 300 + 10, y=pt.y() + 68 + 10)
    with pyautogui.hold('ctrl'):
        pyautogui.press('x')
    wait_until(lambda: len(windows_container.timeline_window.inner_widget.clip_rects) == 2)

    pyautogui.click(x=pt.x() + 50 + 10, y=pt.y() + 68 + 10)
    with pyautogui.hold('ctrl'):
        pyautogui.press('v')
        pyautogui.press('v')
    wait_until(lambda: len(timeline_window.inner_widget.clip_rects) == 4)

    expected_out_frame1 = 1 * 60 * 4
    timeline_clip1 = get_video_clip_for_1hr_vid(out_frame=expected_out_frame1)

    expected_out_frame2 = 2 * 60 * 4
    timeline_clip2 = get_video_clip_for_1hr_vid(in_frame=expected_out_frame1, out_frame=expected_out_frame2)

    expected_out_frame3 = 3 * 60 * 4
    timeline_clip3 = get_video_clip_for_1hr_vid(in_frame=expected_out_frame2, out_frame=expected_out_frame3)

    expected_timeline_clips = [(timeline_clip3,120),(timeline_clip3,120),(timeline_clip1,120),(timeline_clip2,120)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_fn([(video_path, [])]), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_1hr_file_fn(slider_range=(0.04,0.06), current_frame_no=expected_out_frame3, in_frame=expected_out_frame2, out_frame=expected_out_frame3), 
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=0, clipboard_clip=timeline_clip3))

def test_copy_and_paste_clips(app_thread, windows_container: WindowsContainer, blank_state):
    preview_window = windows_container.preview_window
    pw_pt_x, pw_pt_y = get_center_pos_of_widget(preview_window.preview_widget, preview_window)

    video_path = get_blank_1hr_vid_path()
    drop_video_on_file_list(app_thread, windows_container, [video_path])

    video_tab_list_widget = app_thread.mon.tabbed_list_window.videos_tab.list_widget
    item = video_tab_list_widget.get_all_items()[0]
    item_widget = video_tab_list_widget.itemWidget(item)
    pt = local_to_global_pos(item_widget, video_tab_list_widget)
    pyautogui.doubleClick(x=pt.x() + 10, y=pt.y() + 10)
    wait_until(lambda: windows_container.preview_window.preview_widget.cap is not None)
    pyautogui.press('space')
    wait_until(lambda: not windows_container.preview_window.preview_widget.timer.isActive())

    enter_time_in_go_to_dialog_box(app_thread, '0:01:00.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)
    drop_cur_to_timeline(windows_container)
    
    pyautogui.click(x=pw_pt_x + 10, y=pw_pt_y + 10)

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)
    enter_time_in_go_to_dialog_box(app_thread, '0:02:00.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)
    drop_cur_to_timeline(windows_container)

    pyautogui.click(x=pw_pt_x + 10, y=pw_pt_y + 10)

    pyautogui.press('i')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.in_frame is not None)
    enter_time_in_go_to_dialog_box(app_thread, '0:03:00.00')
    pyautogui.press('o')
    wait_until(lambda: app_thread.mon.state.preview_window.frame_in_out.out_frame is not None)
    drop_cur_to_timeline(windows_container)

    timeline_window = windows_container.timeline_window
    pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    pyautogui.click(x=pt.x() + 300 + 10, y=pt.y() + 68 + 10)
    with pyautogui.hold('ctrl'):
        pyautogui.press('c')
    wait_until(lambda: app_thread.mon.state.timeline.clipboard_clip is not None)

    pyautogui.click(x=pt.x() + 200 + 10, y=pt.y() + 68 + 10)
    with pyautogui.hold('ctrl'):
        pyautogui.press('v')
        pyautogui.press('v')
    wait_until(lambda: len(timeline_window.inner_widget.clip_rects) == 5)

    expected_out_frame1 = 1 * 60 * 4
    timeline_clip1 = get_video_clip_for_1hr_vid(out_frame=expected_out_frame1)

    expected_out_frame2 = 2 * 60 * 4
    timeline_clip2 = get_video_clip_for_1hr_vid(in_frame=expected_out_frame1, out_frame=expected_out_frame2)

    expected_out_frame3 = 3 * 60 * 4
    timeline_clip3 = get_video_clip_for_1hr_vid(in_frame=expected_out_frame2, out_frame=expected_out_frame3)

    expected_timeline_clips = [(timeline_clip1,120),(timeline_clip3,120),(timeline_clip3,120),(timeline_clip2,120),(timeline_clip3,120)]

    generic_assert(app_thread, windows_container, blank_state,
            get_assert_file_list_fn([(video_path, [])]), get_assert_blank_list_fn(is_file_list=False), 
            get_assert_preview_for_1hr_file_fn(slider_range=(0.04,0.06), current_frame_no=expected_out_frame3, in_frame=expected_out_frame2, out_frame=expected_out_frame3), 
            get_assert_preview_for_blank_file_fn(is_output_window=True),
            get_assert_timeline_fn(expected_timeline_clips, selected_clip_index=1, clipboard_clip=timeline_clip3))

def hover_over_rect_and_assert(timeline_window, idx: int = 0, assert_threshold: int = 0.9):
    _, rect = timeline_window.inner_widget.clip_rects[idx]
    corner_pt = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    x = int(corner_pt.x() + rect.x() + rect.width() / 2)
    y = int(corner_pt.y() + rect.y() + rect.height() / 2)

    pyautogui.moveTo(int(corner_pt.x() + rect.x() + rect.width() / 2), int(corner_pt.y() + rect.y() + rect.height() / 2))
    time.sleep(1)

    template_img = get_img_asset('hover_template.png')
    screen_img = grab_screenshot((x, y, 100, 100))

    assert cmp_image(screen_img, template_img) >= assert_threshold

def drop_cur_to_timeline(windows_container):
    preview_window = windows_container.preview_window
    src_corner_pt1 = local_to_global_pos(preview_window.preview_widget, preview_window)
    src_pt_x = int(src_corner_pt1.x() + preview_window.width() / 2)
    src_pt_y = int(src_corner_pt1.y() + preview_window.height() / 2)

    timeline_window = windows_container.timeline_window
    dest_corner_pt2 = local_to_global_pos(timeline_window.inner_widget, timeline_window)
    dest_pt_x = int(dest_corner_pt2.x() + timeline_window.width() / 2)
    dest_pt_y = int(dest_corner_pt2.y() + timeline_window.height() / 2)

    drag_and_drop(src_pt_x, src_pt_y, dest_pt_x, dest_pt_y)

    wait_until(lambda: len(timeline_window.inner_widget.clip_rects) > 0)
