import time
import pyautogui
import pytest
from goddo_player.utils.window_util import local_to_global_pos

from goddo_test.utils.command_widget import Command, CommandType
from goddo_test.utils.test_utils import wait_until, cmp_image, pil_img_to_arr
from goddo_test.utils.windows_container import WindowsContainer


def test_all_visible(app_thread):
    assert app_thread.mon.tabbed_list_window.isVisible()
    assert app_thread.mon.preview_window.isVisible()
    assert app_thread.mon.preview_window_output.isVisible()
    assert app_thread.mon.timeline_window.isVisible()

    # cleanup
    wait_until(lambda: app_thread.cmd.queue_is_empty())


# these tests can fail for no reason, when we read it from memory it becomes another image some times.  no idea why.
# according to this stackoverflow, imwrite will keep some data cached so not saving screenshot seems to greatly reduce
# chance of failure (ran it 10 times and haven't failed...yet)
# https://stackoverflow.com/questions/50393741/opencv-python-how-to-avoid-cv2-imwrite-memory-leak-in-py3
@pytest.mark.parametrize("test_win_key", ["tabbed_list_window", "preview_window",
                                          "output_window", "timeline_window"])
def test_show_all_file_window_main(app_thread, windows_container: WindowsContainer, test_win_key, comparison_threshold=0.9):
    submit_cmd = app_thread.cmd.submit_cmd

    windows_dict = windows_container.__dict__

    img_base = pil_img_to_arr(pyautogui.screenshot())
    # save_screenshot(f'screen_{test_win_key}_base.png', img_base)
    # del img_base

    click_main_window(windows_dict[test_win_key])

    submit_cmd(Command(CommandType.SHOW_MAX_WINDOW))
    # submit_cmd(Command(getattr(CommandType, f'ACTIVATE_{test_win_key.upper()}')))

    time.sleep(0.5)

    with pyautogui.hold('alt'):
        pyautogui.press(['tab'])

    wait_until(lambda: getattr(windows_container, test_win_key).isActiveWindow())

    img_new = pil_img_to_arr(pyautogui.screenshot())
    # save_screenshot(f'screen_{test_win_key}_new_before.png', img_new)
    # del img_new

    for k in windows_dict.keys():
        win = windows_dict[k]
        x, y, w, h = win.geometry().getRect()

        # img_base = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_base.png')))
        # img_new = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_new_before.png')))

        new_img = img_new[y:y+h, x:x+w]
        base_img = img_base[y:y+h, x:x+w]
        # save_screenshot(f'visibility_cmp_before_win_{test_win_key}_{k}_new.png', new_img)
        # save_screenshot(f'visibility_cmp_before_win_{test_win_key}_{k}_base.png', base_img)
        if k == test_win_key:
            assert cmp_image(new_img, base_img) > comparison_threshold, f'failed for {test_win_key} - {k}'
        else:
            assert cmp_image(new_img, base_img) < comparison_threshold, f'failed for {test_win_key} - {k}'

    img_new = None
    del img_new

    pyautogui.press('F2')

    wait_until(lambda: len([v for k,v in windows_dict.items() if not v.isMinimized()]) == len(windows_dict))

    img_new = pil_img_to_arr(pyautogui.screenshot())
    # save_screenshot(f'screen_{test_win_key}_new_after.png', img_new)

    for k in windows_dict.keys():
        win = windows_dict[k]
        x, y, w, h = win.geometry().getRect()

        # img_base = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_base.png')))
        # img_new = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_new_after.png')))

        new_img = img_new[y:y + h, x:x + w]
        base_img = img_base[y:y + h, x:x + w]
        # save_screenshot(f'visibility_cmp_after_win_{test_win_key}_{k}_new.png', new_img)
        # save_screenshot(f'visibility_cmp_after_win_{test_win_key}_{k}_base.png', base_img)
        assert cmp_image(new_img, base_img) > comparison_threshold


@pytest.mark.parametrize("test_win_key", ["tabbed_list_window", "preview_window",
                                          "output_window", "timeline_window"])
def test_minimize_and_show_all_file_window_main(app_thread, windows_container: WindowsContainer, test_win_key, comparison_threshold=0.9):
    submit_cmd = app_thread.cmd.submit_cmd

    img_base = pil_img_to_arr(pyautogui.screenshot())

    windows_dict = windows_container.__dict__
    for k in windows_dict.keys():
        if k != test_win_key:
            submit_cmd(Command(CommandType.MINIMIZE_GODDO_WINDOW, [windows_dict[k]]))

    click_main_window(windows_dict[test_win_key])

    img_new = pil_img_to_arr(pyautogui.screenshot())

    for k in windows_dict.keys():
        win = windows_dict[k]
        x, y, w, h = win.geometry().getRect()

        # img_base = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_base.png')))
        # img_new = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_new_before.png')))

        new_img = img_new[y:y+h, x:x+w]
        base_img = img_base[y:y+h, x:x+w]
        # save_screenshot(f'visibility_cmp_before_win_{test_win_key}_{k}_new.png', new_img)
        # save_screenshot(f'visibility_cmp_before_win_{test_win_key}_{k}_base.png', base_img)
        if k == test_win_key:
            assert cmp_image(new_img, base_img) > comparison_threshold, f'failed for {test_win_key} - {k}'
        else:
            assert cmp_image(new_img, base_img) < comparison_threshold, f'failed for {test_win_key} - {k}'

    img_new = None
    del img_new

    pyautogui.press('F2')

    wait_until(lambda: len([v for k,v in windows_dict.items() if not v.isMinimized()]) == len(windows_dict))

    time.sleep(0.5)

    img_new = pil_img_to_arr(pyautogui.screenshot())

    for k in windows_dict.keys():
        win = windows_dict[k]
        x, y, w, h = win.geometry().getRect()

        # img_base = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_base.png')))
        # img_new = cv2.imread(str(output_screenshot_folder_path().joinpath(f'screen_{test_win_key}_new_after.png')))

        new_img = img_new[y:y + h, x:x + w]
        base_img = img_base[y:y + h, x:x + w]
        # save_screenshot(f'visibility_cmp_after_win_{test_win_key}_{k}_new.png', new_img)
        # save_screenshot(f'visibility_cmp_after_win_{test_win_key}_{k}_base.png', base_img)
        assert cmp_image(new_img, base_img) > comparison_threshold


def click_main_window(main_window):
    pos = main_window.pos()
    pyautogui.moveTo(pos.x()+30, pos.y()+10)
    pyautogui.click()