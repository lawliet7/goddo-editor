
import logging
from goddo_player.utils.time_frame_utils import time_str_to_frames
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.video_path import VideoPath
from goddo_test.utils.path_util import video_folder_path
from goddo_test.utils.test_utils import get_test_vid_path, qimg_to_arr, save_reload_and_assert_state, save_screenshot, wait_until


def generic_assert(app_thread, windows_container, blank_state, save_file,
                   fn_assert_file_list, fn_assert_clip_list, fn_assert_preview, fn_assert_output, fn_assert_timeline):

    state_dict = app_thread.mon.state.as_dict()
    win_state_dict = windows_container.as_dict()

    fn_assert_file_list(app_thread, windows_container, state_dict, win_state_dict)
    fn_assert_clip_list(app_thread, windows_container, state_dict, win_state_dict)
    fn_assert_preview(app_thread, windows_container, state_dict, win_state_dict)
    fn_assert_output(app_thread, windows_container, state_dict, win_state_dict)
    fn_assert_timeline(app_thread, windows_container, state_dict , win_state_dict)

    save_reload_and_assert_state(app_thread, windows_container, blank_state, save_file)

def get_assert_file_list_for_test_file_1_fn(ext='mp4', tags=[]):
    video_path = get_test_vid_path(ext)

    def fn1(app_thread, windows_container, state_dict, win_state_dict):
        # assert state
        def assert_file_item(file_item_dict):
            assert file_item_dict['name'] == str(video_path)
            assert file_item_dict['tags'] == []

        for f in state_dict['file_list']['files']:
            assert_file_item(f)

        for k,v in state_dict['file_list']['files_dict'].items():
            assert k == str(video_path)
            assert_file_item(v)

        # assert win state
        assert win_state_dict['tabbed_list_window']['geometry']['x'] == 0
        assert win_state_dict['tabbed_list_window']['geometry']['y'] == 27
        assert win_state_dict['tabbed_list_window']['geometry']['width'] == 546
        assert win_state_dict['tabbed_list_window']['geometry']['height'] == 1000

        clips = win_state_dict['tabbed_list_window']['videos_tab']['clips']
        assert len(clips) == 1

        assert clips[0]['name'] == video_path.file_name()
        assert clips[0]['tags'] == tags

        # wait for screenshot to finish loading
        wait_until(lambda: app_thread.cmd.queue_is_empty())
        videos_tab = windows_container.tabbed_list_window.videos_tab
        video_tab_list_widget = videos_tab.list_widget
        item = video_tab_list_widget.item(video_tab_list_widget.count() - 1)
        item_widget = video_tab_list_widget.itemWidget(item)
        pixmap = item_widget.screenshot_label.pixmap()
        assert pixmap != videos_tab.black_pixmap

    return fn1

def get_assert_blank_list_fn(is_file_list: bool):
    def fn1(app_thread, windows_container, state_dict, win_state_dict):
        if is_file_list:
            # assert state
            assert len(state_dict['file_list']['files']) == 0
            assert len(state_dict['file_list']['files_dict']) == 0

            # assert win state
            assert len(win_state_dict['videos_tab']['clips']) == 0
        else:
            # assert state
            assert len(state_dict['clip_list']['clips']) == 0
            assert len(state_dict['clip_list']['clips_dict']) == 0

            # assert win state
            assert len(win_state_dict['tabbed_list_window']['clips_tab']['clips']) == 0

        assert win_state_dict['tabbed_list_window']['geometry']['x'] == 0
        assert win_state_dict['tabbed_list_window']['geometry']['y'] == 27
        assert win_state_dict['tabbed_list_window']['geometry']['width'] == 546
        assert win_state_dict['tabbed_list_window']['geometry']['height'] == 1000
    return fn1

def get_assert_preview_for_test_file_1_fn(ext='mp4', slider_range=(0.00, 0.15), current_frame_no=None, in_frame=None, out_frame=None, is_max_speed=False,
                                          time_skip_label="5s"):
    video_path = get_test_vid_path(ext)

    video_total_frames = 210
    fps_2_places = 29.97
    total_time_str = '0:00:07.00'

    if current_frame_no is None:
        from_current_frame_no = int(video_total_frames * slider_range[0])
        to_current_frame_no = int(video_total_frames * slider_range[1])
    else:
        from_current_frame_no = to_current_frame_no = current_frame_no

    if 'm' in time_skip_label:
        idx_of_m = time_skip_label.index("m")
        mins = int(time_skip_label[:idx_of_m])
        if 's' in time_skip_label:
            secs = int(time_skip_label[idx_of_m+1:-1])
        else:
            secs = 0
    else:
        mins = 0
        secs = int(time_skip_label[:-1])
    time_skip_multiplier = int((mins * 60 + secs) / 5)

    def fn1(app_thread, windows_container, state_dict, win_state_dict):
        # preview window asserts
        assert state_dict['preview_window']['video_path'] == str(video_path)
        assert round(state_dict['preview_window']['fps'],2) == fps_2_places
        assert state_dict['preview_window']['total_frames'] == video_total_frames
        assert state_dict['preview_window']['frame_in_out']['in_frame'] is in_frame
        assert state_dict['preview_window']['frame_in_out']['out_frame'] is out_frame
        assert from_current_frame_no <= state_dict['preview_window']['current_frame_no'] <= to_current_frame_no
        assert state_dict['preview_window']['is_max_speed'] == is_max_speed
        assert state_dict['preview_window']['time_skip_multiplier'] == time_skip_multiplier
        assert state_dict['preview_window']['cur_total_frames'] == video_total_frames
        assert state_dict['preview_window']['cur_start_frame'] == 0
        assert state_dict['preview_window']['cur_end_frame'] == video_total_frames

        # assert win state preview window
        assert win_state_dict['preview_window']['windowTitle'].endswith(f' - {video_path.file_name(include_ext=False)}')
        assert win_state_dict['preview_window']['geometry']['x'] == 546
        assert win_state_dict['preview_window']['geometry']['y'] == 78
        assert win_state_dict['preview_window']['geometry']['width'] == 640
        assert win_state_dict['preview_window']['geometry']['height'] == 407
        logging.info(win_state_dict['preview_window']['label'])

        time_label, speed_label, skip_label = [x for x in win_state_dict['preview_window']['label'].split(' ') if x.strip() != '']
        max_speed_label = "max" if is_max_speed else "normal"
        assert speed_label.strip() == f'speed={max_speed_label}'
        assert skip_label.strip() == f'skip={time_skip_label}'

        cur_time_label, total_time_label = time_label.split('/')
        assert total_time_label.strip() == total_time_str

        total_frames_in_time_label = time_str_to_frames(cur_time_label,fps_2_places)
        assert int(video_total_frames * slider_range[0]) <= total_frames_in_time_label <= int(video_total_frames * slider_range[1])

        slider_max = windows_container.preview_window.slider.maximum()
        assert win_state_dict['preview_window']['slider']['isEnabled'] == True
        assert slider_max * slider_range[0] <= win_state_dict['preview_window']['slider']['value'] <= slider_max * slider_range[1]
        assert win_state_dict['preview_window']['restrict_frame_interval'] == False

        frame_pixmap = windows_container.preview_window.preview_widget.frame_pixmap
        assert qimg_to_arr(frame_pixmap.toImage()).mean() != 0

        import cv2
        assert state_dict['preview_window']['current_frame_no'] == int(windows_container.preview_window.preview_widget.cap.get(cv2.CAP_PROP_POS_FRAMES))

    return fn1

def get_assert_preview_for_blank_file_fn(is_output_window: bool):
    def fn1(app_thread, windows_container, state_dict, win_state_dict):
        if is_output_window:
            geometry_dict = {
                "x": 1196,
                "y": 78,
                "width": 640,
                "height": 407
            }
            restrict_frame_interval = True
            resolved_state_dict = state_dict['preview_window_output']
            resolved_win_state_dict = win_state_dict['output_window']

            frame_pixmap = windows_container.output_window.preview_widget.frame_pixmap
            assert frame_pixmap is None or qimg_to_arr(frame_pixmap.toImage()).mean() == 0
        else:
            geometry_dict = {
                "x": 546,
                "y": 78,
                "width": 640,
                "height": 407
            }
            restrict_frame_interval = False
            resolved_state_dict = state_dict['preview_window']
            resolved_win_state_dict = win_state_dict['preview_window']

            frame_pixmap = windows_container.preview_window.preview_widget.frame_pixmap
            assert frame_pixmap is None or qimg_to_arr(frame_pixmap.toImage()).mean() == 0

        # state asserts
        assert resolved_state_dict['video_path'] == ''
        assert round(resolved_state_dict['fps'],2) == 0
        assert resolved_state_dict['total_frames'] == 0
        assert resolved_state_dict['frame_in_out']['in_frame'] is None
        assert resolved_state_dict['frame_in_out']['out_frame'] is None
        assert resolved_state_dict['current_frame_no'] == 0
        assert not resolved_state_dict['is_max_speed']
        assert resolved_state_dict['time_skip_multiplier'] == 1
        assert resolved_state_dict['cur_total_frames'] == 0
        assert resolved_state_dict['cur_start_frame'] == 0
        assert resolved_state_dict['cur_end_frame'] == 0

        # win state asserts
        assert ' - clip#' not in win_state_dict['output_window']['windowTitle']
        assert resolved_win_state_dict['geometry'] == geometry_dict
        assert resolved_win_state_dict['label'] == 'you suck'
        assert resolved_win_state_dict['slider']['isEnabled'] == False
        assert resolved_win_state_dict['slider']['value'] == 0
        assert resolved_win_state_dict['restrict_frame_interval'] == restrict_frame_interval
    return fn1

def assert_blank_timeline(app_thread, windows_container, state_dict, win_state_dict):
    # assert timeline
    assert len(state_dict['timeline']['clips']) == 0
    assert state_dict['timeline']['width_of_one_min'] == 120
    assert state_dict['timeline']['selected_clip_index'] == -1
    assert state_dict['timeline']['opened_clip_index'] == -1

     # assert win state timeline
    assert win_state_dict['timeline_window']['geometry']['x'] == 546
    assert win_state_dict['timeline_window']['geometry']['y'] == 525
    assert win_state_dict['timeline_window']['geometry']['width'] == 1075
    assert win_state_dict['timeline_window']['geometry']['height'] == 393
    assert win_state_dict['timeline_window']['innerWidgetSize']['width'] == 1075
    assert win_state_dict['timeline_window']['innerWidgetSize']['height'] == 393
    assert len(win_state_dict['timeline_window']['clip_rects']) == 0

def get_assert_timeline_for_test_file_1_fn(in_frame=None, out_frame=None, width_of_one_min = 120):

    video_path = get_test_vid_path('mp4')

    video_total_frames = 210
    fps_2_places = 29.97
    total_time_str = '0:00:07.00'

    def fn1(app_thread, windows_container, state_dict, win_state_dict):
        # assert timeline
        assert len(state_dict['timeline']['clips']) == 1
        clip = state_dict['timeline']['clips'][0]
        assert clip['video_path'] == str(video_path)
        assert round(clip['fps'],2) == fps_2_places
        assert clip['total_frames'] == video_total_frames
        assert clip['frame_in_out']['in_frame'] == in_frame
        assert clip['frame_in_out']['out_frame'] == out_frame
        assert state_dict['timeline']['width_of_one_min'] == width_of_one_min
        assert state_dict['timeline']['selected_clip_index'] == -1
        assert state_dict['timeline']['opened_clip_index'] == -1
        assert state_dict['timeline']['clipboard_clip'] is None
        
        # assert win state timeline
        assert win_state_dict['timeline_window']['geometry']['x'] == 546
        assert win_state_dict['timeline_window']['geometry']['y'] == 525
        assert win_state_dict['timeline_window']['geometry']['width'] == 1075
        assert win_state_dict['timeline_window']['geometry']['height'] == 393
        assert win_state_dict['timeline_window']['innerWidgetSize']['width'] == 1075
        assert win_state_dict['timeline_window']['innerWidgetSize']['height'] == 393
        assert len(win_state_dict['timeline_window']['clip_rects']) == 1

        clip, rect = win_state_dict['timeline_window']['clip_rects'][0]
        assert clip['video_path'] == str(video_path)
        assert round(clip['fps'],2) == fps_2_places
        assert clip['total_frames'] == video_total_frames
        assert clip['frame_in_out']['in_frame'] == in_frame
        assert clip['frame_in_out']['out_frame'] == out_frame

        resolved_in_frame = in_frame if in_frame else 1
        resolved_out_frame = out_frame if out_frame else video_total_frames
        total_clip_frames = resolved_out_frame - resolved_in_frame + 1
        est_no_of_pixels = total_clip_frames / fps_2_places / 60 * width_of_one_min

        assert rect['x'] == 0
        assert rect['y'] == 68
        assert est_no_of_pixels - 1 <= rect['width'] <= est_no_of_pixels + 1
        assert rect['height'] == 100

    return fn1