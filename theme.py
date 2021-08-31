from dataclasses import dataclass

from PyQt5.QtGui import QColor


@dataclass
class Color:
    controls = QColor(153, 0, 153)
    half_opacity_gray = QColor(191, 191, 191, 50)
    gray = QColor(242, 242, 242)


@dataclass
class Theme:
    color = Color()
