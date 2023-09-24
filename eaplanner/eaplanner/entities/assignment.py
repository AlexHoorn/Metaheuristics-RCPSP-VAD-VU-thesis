from dataclasses import dataclass, field
from itertools import count
import math

asg_id_iter = count()


@dataclass
class Assignment:
    hours: int = 0
    id: int = field(default_factory=lambda: next(asg_id_iter))
    start: int = 0
    _duration: int = field(default=1, init=False)
    _hours_per_day: float | None = field(default=None, init=False)

    # purely for database polling convenience
    activity_id: int = 0

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value: int):
        if value > 1:
            self._duration = value
        else:
            self._duration = 1

        self._set_hours_per_day()

    @property
    def end(self):
        return self.start + self.duration

    @end.setter
    def end(self, value: int):
        self.start = value - self.duration

    def _set_hours_per_day(self):
        hours_per_day = self.hours / self.duration
        self._hours_per_day = math.ceil(hours_per_day)
        return hours_per_day

    @property
    def hours_per_day(self):
        if self._hours_per_day is None:
            return self._set_hours_per_day()

        return self._hours_per_day

    def set(self, start: int, duration: int):
        self.start = start
        self.duration = duration

        # so that we can chain the calls
        return self

    def to_csv_row(self):
        return ",".join(
            str(v) for v in [self.id, self.hours, self.start, self.duration]
        )

    @staticmethod
    def from_csv_row(row: dict[str, str]):
        assignment = Assignment(
            hours=int(row["hours"]), start=int(row["start"]), id=int(row["id"])
        )
        assignment.duration = int(row["duration"])
        return assignment
