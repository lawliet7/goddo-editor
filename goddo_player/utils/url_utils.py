import os

from PyQt5.QtCore import QUrl


# if file_path is not string, we will try to convert it to string before converting to QUrl
def file_to_url(file_path):
    return QUrl.fromLocalFile(str(file_path))


def get_file_name_from_url(url: QUrl):
    return url.fileName().split(os.sep)[-1]
