
import logging
from typing import Dict, List, Tuple
from goddo_player.app.app_constants import WINDOW_NAME_OUTPUT, WINDOW_NAME_SOURCE
from goddo_player.app.player_configs import PlayerConfigs
from goddo_player.app.state_store import VideoClip
from goddo_player.utils.time_frame_utils import is_time_label, time_str_to_frames
from goddo_player.utils.url_utils import file_to_url
from goddo_player.utils.video_path import VideoPath
from goddo_test.utils.path_util import video_folder_path
from goddo_test.utils.test_utils import get_blank_1hr_vid_path, get_current_method_name, get_test_vid_path, qimg_to_arr, save_reload_and_assert_state, save_screenshot, wait_until


def generic_assert(app_thread, windows_container, blank_state,
                   fn_assert_file_list, fn_assert_clip_list, fn_assert_preview, fn_assert_output, fn_assert_timeline, 
                   save_file='<file_name>.<method_name>.json'):

    file_name, method_name = get_current_method_name(2)
    resolved_save_file = save_file.replace('<file_name>', file_name).replace('<method_name>', method_name)
    logging.info(resolved_save_file)

    state_dict = app_thread.mon.state.as_dict()
    win_state_dict = windows_container.as_dict()

    fn_assert_file_list(app_thread, windows_container, state_dict, win_state_dict)
    fn_assert_clip_list(app_thread, windows_container, state_dict, win_state_dict)
    fn_assert_preview(app_thread, windows_container, state_dict, win_state_dict)
    fn_assert_output(app_thread, windows_container, state_dict, win_state_dict)
    fn_assert_timeline(app_thread, windows_container, state_dict , win_state_dict)

    save_reload_and_assert_state(app_thread, windows_container, blank_state, resolved_save_file)

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

def get_assert_file_list_for_1hr_fn(tags=[]):
    video_path = get_blank_1hr_vid_path()

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

def get_assert_file_list_fn(videos: List[Tuple[VideoPath,List[str]]]):
    def fn1(app_thread, windows_container, state_dict, win_state_dict):
        # assert state
        assert len(state_dict['file_list']['files']) == len(videos)
        assert len(state_dict['file_list']['files_dict']) == len(videos)

        for i, (video_path, tags) in enumerate(videos):
            assert state_dict['file_list']['files'][i]['name'] == str(video_path)
            assert state_dict['file_list']['files'][i]['tags'] == tags

            assert state_dict['file_list']['files_dict'][str(video_path)]['name'] == str(video_path)
            assert state_dict['file_list']['files_dict'][str(video_path)]['tags'] == tags

        # assert win state
        assert win_state_dict['tabbed_list_window']['geometry']['x'] == 0
        assert win_state_dict['tabbed_list_window']['geometry']['y'] == 27
        assert win_state_dict['tabbed_list_window']['geometry']['width'] == 546
        assert win_state_dict['tabbed_list_window']['geometry']['height'] == 1000

        clips = win_state_dict['tabbed_list_window']['videos_tab']['clips']
        assert len(clips) == len(videos)

        for i, (video_path, tags) in enumerate(videos):
            assert clips[i]['name'] == video_path.file_name()
            assert clips[i]['tags'] == tags

        # wait for screenshot to finish loading
        wait_until(lambda: app_thread.cmd.queue_is_empty())
        videos_tab = windows_container.tabbed_list_window.videos_tab
        video_tab_list_widget = videos_tab.list_widget
        item = video_tab_list_widget.item(video_tab_list_widget.count() - 1)
        item_widget = video_tab_list_widget.itemWidget(item)
        pixmap = item_widget.screenshot_label.pixmap()
        assert pixmap != videos_tab.black_pixmap

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
        assert state_dict['preview_window']['frame_in_out']['in_frame'] == in_frame
        assert state_dict['preview_window']['frame_in_out']['out_frame'] == out_frame
        assert from_current_frame_no <= state_dict['preview_window']['current_frame_no'] <= to_current_frame_no
        assert state_dict['preview_window']['is_max_speed'] == is_max_speed
        assert state_dict['preview_window']['time_skip_multiplier'] == time_skip_multiplier
        assert state_dict['preview_window']['cur_total_frames'] == video_total_frames
        assert state_dict['preview_window']['cur_start_frame'] == 1
        assert state_dict['preview_window']['cur_end_frame'] == video_total_frames

        # assert win state preview window
        assert win_state_dict['preview_window']['windowTitle'].endswith(f' - {video_path.file_name(include_ext=False)}')
        assert win_state_dict['preview_window']['geometry']['x'] == 546
        assert win_state_dict['preview_window']['geometry']['y'] == 78
        assert win_state_dict['preview_window']['geometry']['width'] == 640
        assert win_state_dict['preview_window']['geometry']['height'] == 407

        max_speed_label = "max" if is_max_speed else "normal"
        assert win_state_dict['preview_window']['speed_label'] == f'speed={max_speed_label}'
        assert win_state_dict['preview_window']['skip_label'] == f'skip={time_skip_label}'

        cur_time_label, total_time_label = win_state_dict['preview_window']['time_label'].split('/')
        assert total_time_label.strip() == total_time_str

        total_frames_in_time_label = time_str_to_frames(cur_time_label,fps_2_places)
        assert int(video_total_frames * slider_range[0]) <= total_frames_in_time_label <= int(video_total_frames * slider_range[1])

        slider_max = windows_container.preview_window.slider.maximum()
        assert win_state_dict['preview_window']['slider']['isEnabled'] == True
        assert slider_max * slider_range[0] <= win_state_dict['preview_window']['slider']['value'] <= slider_max * slider_range[1]

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
        assert resolved_win_state_dict['time_label'] == '0:00:00.00/0:00:00.00'
        assert resolved_win_state_dict['speed_label'] == 'speed=normal'
        assert resolved_win_state_dict['skip_label'] == 'skip=5s'
        assert resolved_win_state_dict['vol_label'] == 'vol=100%'

        assert resolved_win_state_dict['slider']['isEnabled'] == False
        assert resolved_win_state_dict['slider']['value'] == 0
    return fn1

def get_assert_preview_for_1hr_file_fn(slider_range=(0.00, 0.01), current_frame_no=None, in_frame=None, out_frame=None, is_max_speed=False,
                                          time_skip_label="5s"):
    video_path = get_blank_1hr_vid_path()

    video_total_frames = 14402
    fps = 4
    total_time_str = '1:00:00.02'

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
        assert state_dict['preview_window']['fps'] == fps
        assert state_dict['preview_window']['total_frames'] == video_total_frames
        assert state_dict['preview_window']['frame_in_out']['in_frame'] == in_frame
        assert state_dict['preview_window']['frame_in_out']['out_frame'] == out_frame
        assert from_current_frame_no <= state_dict['preview_window']['current_frame_no'] <= to_current_frame_no
        assert state_dict['preview_window']['is_max_speed'] == is_max_speed
        assert state_dict['preview_window']['time_skip_multiplier'] == time_skip_multiplier
        assert state_dict['preview_window']['cur_total_frames'] == video_total_frames
        assert state_dict['preview_window']['cur_start_frame'] == 1
        assert state_dict['preview_window']['cur_end_frame'] == video_total_frames

        # assert win state preview window
        assert win_state_dict['preview_window']['windowTitle'].endswith(f' - {video_path.file_name(include_ext=False)}')
        assert win_state_dict['preview_window']['geometry']['x'] == 546
        assert win_state_dict['preview_window']['geometry']['y'] == 78
        assert win_state_dict['preview_window']['geometry']['width'] == 640
        assert win_state_dict['preview_window']['geometry']['height'] == 407

        max_speed_label = "max" if is_max_speed else "normal"
        assert win_state_dict['preview_window']['speed_label'] == f'speed={max_speed_label}'
        assert win_state_dict['preview_window']['skip_label'] == f'skip={time_skip_label}'

        cur_time_label, total_time_label = win_state_dict['preview_window']['time_label'].split('/')
        assert total_time_label.strip() == total_time_str

        total_frames_in_time_label = time_str_to_frames(cur_time_label,fps)
        assert int(video_total_frames * slider_range[0]) <= total_frames_in_time_label <= int(video_total_frames * slider_range[1])

        slider_max = windows_container.preview_window.slider.maximum()
        assert win_state_dict['preview_window']['slider']['isEnabled'] == True
        assert slider_max * slider_range[0] <= win_state_dict['preview_window']['slider']['value'] <= slider_max * slider_range[1]

        frame_pixmap = windows_container.preview_window.preview_widget.frame_pixmap
        assert qimg_to_arr(frame_pixmap.toImage()).mean() != 0

        import cv2
        assert state_dict['preview_window']['current_frame_no'] == int(windows_container.preview_window.preview_widget.cap.get(cv2.CAP_PROP_POS_FRAMES))

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

def parse_preview_window_label(pw_dict: Dict, window_name: str):
    clean_label_text = pw_dict['time_label']
    time_color = ''
    if '<span' in clean_label_text:
        idx1 = clean_label_text.find('<span')
        idx2 = clean_label_text.find('>', idx1)

        idx3 = clean_label_text.find(':', idx1)
        idx4 = clean_label_text.find(';', idx3)
        time_color = clean_label_text[idx3+1:idx4]

        clean_label_text = clean_label_text[:idx1] + clean_label_text[idx2+1:]

    if '</span>' in clean_label_text:
        idx1 = clean_label_text.find('</span>')
        clean_label_text = clean_label_text[:idx1] + clean_label_text[idx1+7:]

    logging.info(f'label parsed {clean_label_text}')

    if window_name == WINDOW_NAME_OUTPUT:
        logging.info(f'=== label {clean_label_text}')
        cur_abs_time, _, tmp_rel_total_time = [x for x in clean_label_text.split(' ') if x.strip() != '']
        cur_rel_time, total_time = tmp_rel_total_time.split('/')
        return cur_abs_time, cur_rel_time, total_time, pw_dict['speed_label'], pw_dict['skip_label'], pw_dict['restrict_label'], time_color
    elif window_name == WINDOW_NAME_SOURCE:
        cur_abs_time, total_time = clean_label_text.split('/')
        return cur_abs_time, '', total_time, pw_dict['speed_label'], pw_dict['skip_label'], '', time_color
    else:
        raise Exception(f'unhandled window {window_name}')

def get_assert_preview_fn(clip: VideoClip, slider_range=(0.00, 0.01), current_frame_no=None, is_max_speed=False, extra_frames_left=0, extra_frames_right=0,
                          restrict_frame_interval=None, time_skip_label="5s", is_output_window=False, expected_color=95.5):
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
        if is_output_window:
            geometry_dict = {
                "x": 1196,
                "y": 78,
                "width": 640,
                "height": 407
            }
            defaulted_restrict_frame_interval = True if restrict_frame_interval is None else restrict_frame_interval
            resolved_state_dict = state_dict['preview_window_output']
            resolved_win_state_dict = win_state_dict['output_window']
            preview_window = windows_container.output_window
            cur_abs_time_label, cur_rel_time_label, total_time_label, speed_label, skip_label, restrict_label, time_color = \
                parse_preview_window_label(resolved_win_state_dict, WINDOW_NAME_OUTPUT)
            defaulted_restrict_label = f'restrict={defaulted_restrict_frame_interval if restrict_frame_interval is None else restrict_frame_interval}'
            clip_total_frames = clip.frame_in_out.get_no_of_frames(clip.total_frames)
            cur_total_frames = clip.frame_in_out.get_no_of_frames(clip.total_frames) + extra_frames_left + extra_frames_right
            cur_start_frame = clip.frame_in_out.get_resolved_in_frame() - extra_frames_left
            cur_end_frame = clip.frame_in_out.get_resolved_out_frame(clip.total_frames) + extra_frames_right
            logging.info(f'=== label clip total {clip_total_frames} no frames {clip.frame_in_out.get_no_of_frames(clip.total_frames)} frame_in_out {clip.frame_in_out} total {clip.total_frames} label {clip.get_total_time_str(clip_total_frames)}')
            expected_total_time_label = clip.get_total_time_str(clip_total_frames - 1)
        else:
            geometry_dict = {
                "x": 546,
                "y": 78,
                "width": 640,
                "height": 407
            }
            defaulted_restrict_frame_interval = False if restrict_frame_interval is None else restrict_frame_interval
            resolved_state_dict = state_dict['preview_window']
            resolved_win_state_dict = win_state_dict['preview_window']
            preview_window = windows_container.preview_window
            cur_abs_time_label, cur_rel_time_label, total_time_label, speed_label, skip_label, restrict_label, time_color = \
                parse_preview_window_label(resolved_win_state_dict, WINDOW_NAME_SOURCE)
            defaulted_restrict_label = '' if restrict_label is None else restrict_label
            clip_total_frames = clip.total_frames
            cur_total_frames = clip_total_frames
            cur_start_frame = 1
            cur_end_frame = clip_total_frames
            expected_total_time_label = clip.get_total_time_str()

        # preview window asserts
        assert resolved_state_dict['video_path'] == str(clip.video_path)
        assert resolved_state_dict['fps'] == clip.fps
        assert resolved_state_dict['total_frames'] == clip.total_frames
        assert resolved_state_dict['frame_in_out']['in_frame'] == clip.frame_in_out.in_frame
        assert resolved_state_dict['frame_in_out']['out_frame'] == clip.frame_in_out.out_frame
        
        cur_abs_frames_in_time_label = time_str_to_frames(cur_abs_time_label, clip.fps)
        if current_frame_no:
            assert resolved_state_dict['current_frame_no'] == current_frame_no
            assert cur_abs_frames_in_time_label == current_frame_no
        else:
            from_slider_value = int(resolved_state_dict['cur_total_frames'] * slider_range[0] + resolved_state_dict['cur_start_frame'] - 1)
            to_slider_value = int(resolved_state_dict['cur_total_frames'] * slider_range[1] + resolved_state_dict['cur_start_frame'] - 1)
            logging.info(f'=== from slider {from_slider_value} to slider {to_slider_value} cur frame {resolved_state_dict["current_frame_no"]}')
            logging.debug(f"=== cur {resolved_state_dict['current_frame_no']} start {resolved_state_dict['cur_start_frame']} total {resolved_state_dict['cur_total_frames']} range {slider_range}")
            assert from_slider_value <= resolved_state_dict['current_frame_no'] <= to_slider_value
            assert from_slider_value <= cur_abs_frames_in_time_label <= to_slider_value

        assert resolved_state_dict['is_max_speed'] == is_max_speed
        logging.info(f'=== resolved {resolved_state_dict}')
        assert resolved_state_dict['cur_total_frames'] == cur_total_frames
        assert resolved_state_dict['time_skip_multiplier'] == time_skip_multiplier
        assert resolved_state_dict['cur_start_frame'] == cur_start_frame
        assert resolved_state_dict['cur_end_frame'] == cur_end_frame

        # assert win state preview window
        assert resolved_win_state_dict['windowTitle'].endswith(f' - {clip.video_path.file_name(include_ext=False)}')
        assert resolved_win_state_dict['geometry'] == geometry_dict

        max_speed_label = "max" if is_max_speed else "normal"
        assert speed_label.strip() == f'speed={max_speed_label}'
        assert skip_label.strip() == f'skip={time_skip_label}'
        logging.info(f'=== restrict label {restrict_label.strip()} test restrict label {defaulted_restrict_label}')
        assert restrict_label.strip() == defaulted_restrict_label

        # cur_time_label, total_time_label = a_time_label.split('/')
        assert total_time_label.strip() == expected_total_time_label

        if is_output_window:
            cur_rel_frames_in_time_label = time_str_to_frames(cur_rel_time_label, clip.fps)
            cur_total_frames_in_time_label = time_str_to_frames(total_time_label, clip.fps)
            logging.info(f'=== abs {cur_abs_frames_in_time_label} rel {cur_rel_frames_in_time_label} in {clip.frame_in_out.in_frame}')
            assert cur_abs_frames_in_time_label == (cur_rel_frames_in_time_label + clip.frame_in_out.get_resolved_in_frame())

            if resolved_state_dict['current_frame_no'] < clip.frame_in_out.get_resolved_in_frame():
                assert cur_rel_frames_in_time_label < 0
                assert time_color == 'blue'
            if resolved_state_dict['current_frame_no'] > clip.frame_in_out.get_resolved_out_frame(clip.total_frames):
                logging.info(f"=== cur {resolved_state_dict['current_frame_no']} out {clip.frame_in_out.get_resolved_out_frame(clip.total_frames)} rel {cur_rel_frames_in_time_label} total {cur_total_frames_in_time_label}")
                assert cur_rel_frames_in_time_label > cur_total_frames_in_time_label
                assert time_color == 'blue'
        else:
            assert time_color == ''

        slider_max = preview_window.slider.maximum()
        assert resolved_win_state_dict['slider']['isEnabled'] == True
        assert int(round(slider_max * slider_range[0])) <= resolved_win_state_dict['slider']['value'] <= int(round(slider_max * slider_range[1]))

        frame_pixmap = preview_window.preview_widget.frame_pixmap
        assert qimg_to_arr(frame_pixmap.toImage()).mean() != 0

        import cv2
        assert resolved_state_dict['current_frame_no'] == int(preview_window.preview_widget.cap.get(cv2.CAP_PROP_POS_FRAMES))

        frame_pixmap = preview_window.preview_widget.frame_pixmap
        assert frame_pixmap is None or qimg_to_arr(frame_pixmap.toImage()).mean() == expected_color

    return fn1

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
        assert win_state_dict['timeline_window']['geometry']['width'] == PlayerConfigs.timeline_initial_width
        assert win_state_dict['timeline_window']['geometry']['height'] == 393
        assert win_state_dict['timeline_window']['innerWidgetSize']['width'] == PlayerConfigs.timeline_initial_width
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

def get_assert_timeline_for_1hr_file_fn(in_frame=None, out_frame=None, width_of_one_min = 120, num_of_clips=1, selected_clip_index=-1,
                                        clip_rect_widths: List[int] = [0], scroll_area_width=PlayerConfigs.timeline_initial_width):
    video_path = get_blank_1hr_vid_path()

    video_total_frames = 14402
    fps = 4
    total_time_str = '1:00:00.02'

    def fn1(app_thread, windows_container, state_dict, win_state_dict):
        # assert timeline
        assert len(state_dict['timeline']['clips']) == num_of_clips

        for clip in state_dict['timeline']['clips']:
            assert clip['video_path'] == str(video_path)
            assert clip['fps'] == fps
            assert clip['total_frames'] == video_total_frames
            assert clip['frame_in_out']['in_frame'] == in_frame
            assert clip['frame_in_out']['out_frame'] == out_frame
            assert state_dict['timeline']['width_of_one_min'] == width_of_one_min
            assert state_dict['timeline']['selected_clip_index'] == selected_clip_index
            assert state_dict['timeline']['opened_clip_index'] == -1
            assert state_dict['timeline']['clipboard_clip'] is None
        
        # assert win state timeline
        assert win_state_dict['timeline_window']['geometry']['x'] == 546
        assert win_state_dict['timeline_window']['geometry']['y'] == 525
        assert win_state_dict['timeline_window']['geometry']['width'] == PlayerConfigs.timeline_initial_width
        assert win_state_dict['timeline_window']['geometry']['height'] == 393
        assert win_state_dict['timeline_window']['innerWidgetSize']['width'] == scroll_area_width
        assert win_state_dict['timeline_window']['innerWidgetSize']['height'] == 393
        assert len(win_state_dict['timeline_window']['clip_rects']) == num_of_clips

        x = 0
        for i, (clip, rect) in enumerate(win_state_dict['timeline_window']['clip_rects']):
            assert clip['video_path'] == str(video_path)
            assert clip['fps'] == fps
            assert clip['total_frames'] == video_total_frames
            assert clip['frame_in_out']['in_frame'] == in_frame
            assert clip['frame_in_out']['out_frame'] == out_frame

            assert rect['x'] == x
            assert rect['y'] == 68
            assert rect['width'] == clip_rect_widths[i]
            assert rect['height'] == 100
            x = x + clip_rect_widths[i]

    return fn1

def get_assert_timeline_fn(expected_timeline_clips: List[Tuple[VideoClip,int]], width_of_one_min = 120, selected_clip_index=-1, opened_clip_index=-1,
                                        clipboard_clip: VideoClip = None, scroll_area_width=PlayerConfigs.timeline_initial_width):
    def fn1(app_thread, windows_container, state_dict, win_state_dict):
        # assert timeline
        assert len(state_dict['timeline']['clips']) == len(expected_timeline_clips)

        for i, (timeline_clip, _) in enumerate(expected_timeline_clips):
            clip = state_dict['timeline']['clips'][i]
            assert clip == timeline_clip.as_dict()

        assert state_dict['timeline']['width_of_one_min'] == width_of_one_min
        assert state_dict['timeline']['selected_clip_index'] == selected_clip_index
        assert state_dict['timeline']['opened_clip_index'] == opened_clip_index
        assert state_dict['timeline']['clipboard_clip'] == (clipboard_clip.as_dict() if clipboard_clip else None)
        
        # assert win state timeline
        assert win_state_dict['timeline_window']['geometry']['x'] == 546
        assert win_state_dict['timeline_window']['geometry']['y'] == 525
        assert win_state_dict['timeline_window']['geometry']['width'] == PlayerConfigs.timeline_initial_width
        assert win_state_dict['timeline_window']['geometry']['height'] == 393

        assert win_state_dict['timeline_window']['innerWidgetSize']['width'] == scroll_area_width
        assert win_state_dict['timeline_window']['innerWidgetSize']['height'] == 393
        assert len(win_state_dict['timeline_window']['clip_rects']) == len(expected_timeline_clips)

        x = 0
        for i, (timeline_clip, clip_width) in enumerate(expected_timeline_clips):
            clip, rect = win_state_dict['timeline_window']['clip_rects'][i]

            assert clip == timeline_clip.as_dict()

            assert rect['x'] == x
            assert rect['y'] == 68
            assert rect['width'] == clip_width
            assert rect['height'] == 100
            x = x + clip_width

    return fn1

def assert_go_to_frame_dialog(preview_window, fps, start, end):
    assert preview_window.dialog.dialog_fps_text.text() == f'fps:   {round(fps,3)}'
    assert preview_window.dialog.dialog_start_text.text() == f'start: {start}'
    assert preview_window.dialog.dialog_end_text.text() == f'end:  {end}'
