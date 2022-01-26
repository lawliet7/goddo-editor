from enum import Enum, unique, auto


@unique
class PositionType(Enum):
    ABSOLUTE = auto()
    RELATIVE = auto()


@unique
class IncDec(Enum):
    INC = 1
    DEC = -1
