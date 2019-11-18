from enum import Enum


class Phases(Enum):
    IDLE = 0
    MERGE = 1
    VOTING = 2
    FINALIZE = 3

    def next(self):
        return Phases((self.value + 1) % 4)
