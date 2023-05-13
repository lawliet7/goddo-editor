import os
from pathlib import Path

def is_non_empty_file(file_path):
    return os.path.exists(file_path) and os.stat(file_path).st_size > 0

def get_home_directory():
    if os.name == "nt":
        return os.environ["HOMEDRIVE"] + os.environ["HOMEPATH"]
    else:
        return os.path.expanduser("~")

def get_default_screenshot_folder() -> str:
    home_dir = get_home_directory()
    if 'Pictures' in os.listdir(home_dir):
        return home_dir + os.sep + 'Pictures'
    elif 'pictures' in os.listdir(home_dir):
        return home_dir + os.sep + 'pictures'
    elif 'pics' in os.listdir(home_dir):
        return home_dir + os.sep + 'pics'
    elif 'pic' in os.listdir(home_dir):
        return home_dir + os.sep + 'pic'
    else:
        return home_dir
    
def get_default_screenshot_folder_path() -> Path:
    return Path(get_default_screenshot_folder())