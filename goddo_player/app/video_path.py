import re
import typing

from PyQt5.QtCore import QUrl


class VideoPath:

    # @typing.overload
    # def __init__(self, path: str) -> None:
    #     self.url = QUrl.fromLocalFile(path)

    # @typing.overload
    def __init__(self, url: QUrl) -> None:
        self.url = url

    def path(self):
        p = self.url.path()
        if re.match('^/[a-zA-Z]:', p):
            return p[1:]
        else:
            return p

