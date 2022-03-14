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

    def __eq__(self, o: object) -> bool:
        if isinstance(o, VideoPath):
            return self.str() == o.str()

        return False

    def file_name(self, include_ext=True):
        if include_ext:
            return self.url().fileName()
        else:
            return os.path.splitext(self.file_name())[0]

    def ext(self):
        return os.path.splitext(self.file_name())[1]

    def is_empty(self):
        return self.str() == ''

