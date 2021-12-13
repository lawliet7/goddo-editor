from enum import Enum, unique, auto


@unique
class PositionType(Enum):
    ABSOLUTE = auto()
    RELATIVE = auto()
