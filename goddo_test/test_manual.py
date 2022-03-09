import cv2
import pyautogui
import pytest

from goddo_test.utils.command_widget import Command
from goddo_test.utils.path_util import output_screenshot_folder_path
from goddo_test.utils.test_utils import wait_until, cmp_image, save_screenshot, pil_img_to_arr


def test_all_visible(app_thread):
    assert app_thread.mon.tabbed_list_window.isVisible()
    assert app_thread.mon.preview_window.isVisible()
    assert app_thread.mon.preview_window_output.isVisible()
    assert app_thread.mon.timeline_window.isVisible()

    # cleanup
    wait_until(lambda: app_thread.cmd.queue_is_empty())


# these tests can fail for no reason, when we read it from memory it becomes another image some times.  no idea why.
@pytest.mark.parametrize("test_win_key", ['TABBED_LIST_WINDOW', 'PREVIEW_WINDOW', 'OUTPUT_WINDOW', 'TIMELINE_WINDOW'])
def test_show_all_file_window_main(app_thread, windows_dict, test_win_key, comparison_threshold=0.9):
    submit_cmd = app_thread.cmd.submit_cmd

    img_base = pil_img_to_arr(pyautogui.screenshot())
    save_screenshot(f'screen_{test_win_key}_base.png', img_base)
    del img_base

    submit_cmd(Command.SHOW_MAX_WINDOW)
    submit_cmd(getattr(Command, f'ACTIVATE_{test_win_key}'))

    wait_until(lambda: windows_dict[test_win_key].isActiveWindow())

    img_new = pil_img_to_arr(pyautogui.screenshot())
    save_screenshot(f'screen_{test_win_key}_new_before.png', img_new)
    del img_new

    for k in windows_dict.keys():
        win = windows_dict[k]
        x, y, w, h = win.geometry().getRect()

        img_base = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_base.png')))
        img_new = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_new_before.png')))

        new_img = img_new[y:y+h, x:x+w]
        base_img = img_base[y:y+h, x:x+w]
        save_screenshot(f'visibility_cmp_before_win_{test_win_key}_{k}_new.png', new_img)
        save_screenshot(f'visibility_cmp_before_win_{test_win_key}_{k}_base.png', base_img)
        if k == test_win_key:
            assert cmp_image(new_img, base_img) > comparison_threshold, f'failed for {test_win_key} - {k}'
        else:
            assert cmp_image(new_img, base_img) < comparison_threshold, f'failed for {test_win_key} - {k}'

    pyautogui.press('F2')

    img_new = pil_img_to_arr(pyautogui.screenshot())
    save_screenshot(f'screen_{test_win_key}_new_after.png', img_new)

    for k in windows_dict.keys():
        win = windows_dict[k]
        x, y, w, h = win.geometry().getRect()

        img_base = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_base.png')))
        img_new = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_new_after.png')))

        new_img = img_new[y:y + h, x:x + w]
        base_img = img_base[y:y + h, x:x + w]
        save_screenshot(f'visibility_cmp_after_win_{test_win_key}_{k}_new.png', new_img)
        save_screenshot(f'visibility_cmp_after_win_{test_win_key}_{k}_base.png', base_img)
        assert cmp_image(new_img, base_img) > comparison_threshold


