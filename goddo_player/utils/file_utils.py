import os

def is_non_empty_file(file_path):
    return os.path.exists(file_path) and os.stat(file_path).st_size > 0
