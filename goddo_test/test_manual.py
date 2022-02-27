

def test_all_visible(app_thread):
    assert app_thread.mon.tabbed_list_window.isVisible()
    assert app_thread.mon.preview_window.isVisible()
    assert app_thread.mon.preview_window_output.isVisible()
    assert app_thread.mon.timeline_window.isVisible()
