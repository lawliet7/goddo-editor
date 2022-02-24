import os
import re
import typing
from pathlib import Path

from PyQt5.QtCore import QUrl


class VideoPath:

    # @typing.overload
    # def __init__(self, path: str) -> None:
    #     self.url = QUrl.fromLocalFile(path)

    # @typing.overload
    def __init__(self, url: QUrl) -> None:
        self.__url = url

    def url(self) -> QUrl:
        return self.__url

    def str(self) -> str:
        p = self.url().path()
        if re.match('^/[a-zA-Z]:', p):
            return p[1:]
        else:
            return p

    def path(self) -> Path:
        return Path(self.str())

    def __str__(self) -> str:
        return self.str()

    def __repr__(self) -> str:
        return self.str()

    def file_name(self):
        return self.url().fileName()

    def ext(self):
        _, ext = os.path.splitext(self.file_name())
        return ext

