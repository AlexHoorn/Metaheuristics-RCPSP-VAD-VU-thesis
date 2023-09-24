from enum import Enum


class DateType(Enum):
    AS_SOON_AS_POSSIBLE = 0
    AS_LATE_AS_POSSIBLE = 1
    MUST_START_ON = 2
    MUST_FINISH_ON = 3
    START_NO_EARLIER_THAN = 4
    START_NO_LATER_THAN = 5
    FINISH_NO_EARLIER_THAN = 6
    FINISH_NO_LATER_THAN = 7

    @property
    def short_name(self):
        return "".join([n[0] for n in self.name.split("_")])


class RelationType(Enum):
    FINISH_TO_FINISH = 0
    FINISH_TO_START = 1
    START_TO_FINISH = 2
    START_TO_START = 3

    @property
    def short_name(self):
        return "".join([n[0] for n in self.name.split("_TO_")])
