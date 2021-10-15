from PyQt5.QtCore import QRect


def midpoint(value1, value2, should_round=False):
    if should_round:
        return int(round((value1 + value2) / 2))
    else:
        return int((value1 + value2) / 2)


def scale_rect(rect: QRect, pct):
    top = rect.height() * pct + rect.top()
    left = rect.width() * pct + rect.left()
    width = rect.width() - 2 * pct * rect.width()
    height = rect.height() - 2 * pct * rect.height()
    return QRect(left, top, width, height)


