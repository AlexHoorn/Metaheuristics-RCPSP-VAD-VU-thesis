from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
import math

from matplotlib import patches
from matplotlib.axes import Axes

from eaplanner.entities.assignment import Assignment
from eaplanner.entities.enum import DateType, RelationType
from eaplanner.entities.resource import Resource


class BaseConstraint(ABC):
    @abstractmethod
    def get_penalty(self) -> int:
        # positive penalty means that the constraint is violated
        raise NotImplementedError

    @abstractmethod
    def get_assignments(self) -> list[Assignment]:
        raise NotImplementedError

    @abstractmethod
    def visualize_gantt(self, ax: Axes) -> Axes:
        raise NotImplementedError

    @abstractmethod
    def attempt_repair(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_empty(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def to_csv_row(self) -> str:
        raise NotImplementedError


@dataclass
class RelationConstraint(BaseConstraint):
    type: RelationType
    predecessor: Assignment
    successor: Assignment

    def get_penalty(self):
        match self.type:
            case RelationType.FINISH_TO_FINISH:
                penalty = self.predecessor.end - self.successor.end
            case RelationType.FINISH_TO_START:
                penalty = self.predecessor.end - self.successor.start
            case RelationType.START_TO_FINISH:
                penalty = self.successor.end - self.predecessor.start
            case RelationType.START_TO_START:
                penalty = self.predecessor.start - self.successor.start
            case _:
                raise NotImplementedError

        if penalty < 0:
            return 0

        return penalty

    def get_assignments(self):
        return [self.predecessor, self.successor]

    def attempt_repair(self):
        match self.type:
            case RelationType.FINISH_TO_FINISH:
                if self.predecessor.end > self.successor.end:
                    self.successor.end = self.predecessor.end
                    return True
            case RelationType.FINISH_TO_START:
                if self.predecessor.end > self.successor.start:
                    self.successor.start = self.predecessor.end
                    return True
            case RelationType.START_TO_FINISH:
                if self.successor.end > self.predecessor.start:
                    self.successor.end = self.predecessor.start
                    return True
            case RelationType.START_TO_START:
                if self.predecessor.start > self.successor.start:
                    self.successor.start = self.predecessor.start
                    return True
            case _:
                raise NotImplementedError

        return False

    def is_empty(self):
        if self.predecessor is None or self.successor is None:
            return True

        return False

    def visualize_gantt(self, ax: Axes):
        # draw relation
        match self.type:
            case RelationType.FINISH_TO_FINISH:
                arrow_start = self.predecessor.end
                arrow_end = self.successor.end - self.predecessor.end
            case RelationType.FINISH_TO_START:
                arrow_start = self.predecessor.end
                arrow_end = self.successor.start - self.predecessor.end
            case RelationType.START_TO_FINISH:
                arrow_start = self.predecessor.start
                arrow_end = self.successor.end - self.predecessor.start
            case RelationType.START_TO_START:
                arrow_start = self.predecessor.start
                arrow_end = self.successor.start - self.predecessor.start
            case _:
                raise NotImplementedError

        # draw line
        ax.plot(
            [arrow_start, arrow_start + arrow_end],
            [self.predecessor.id + 0.5, self.successor.id + 0.5],
            color="k" if self.get_penalty() <= 0 else "r",
            ls="solid" if self.get_penalty() <= 0 else "dotted",
            zorder=2,
        )

        return ax

    def to_csv_row(self):
        return ",".join(
            str(v) for v in [self.predecessor.id, self.successor.id, self.type.value]
        )

    @staticmethod
    def from_csv_row(row: dict[str, str], assignments: list[Assignment]):
        predecessor = next(a for a in assignments if a.id == int(row["predecessor_id"]))
        successor = next(a for a in assignments if a.id == int(row["successor_id"]))
        return RelationConstraint(
            type=RelationType(int(row["type"])),
            predecessor=predecessor,
            successor=successor,
        )


@dataclass
class DateConstraint(BaseConstraint):
    type: DateType
    assignment: Assignment
    day: int

    def get_constraint_day(self):
        match self.type:
            case DateType.AS_SOON_AS_POSSIBLE:
                return self.assignment.start
            case DateType.AS_LATE_AS_POSSIBLE:
                return self.assignment.end
            case DateType.MUST_START_ON:
                return self.assignment.start
            case DateType.MUST_FINISH_ON:
                return self.assignment.end
            case DateType.START_NO_EARLIER_THAN:
                return self.assignment.start
            case DateType.START_NO_LATER_THAN:
                return self.assignment.start
            case DateType.FINISH_NO_EARLIER_THAN:
                return self.assignment.end
            case DateType.FINISH_NO_LATER_THAN:
                return self.assignment.end
            case _:
                raise NotImplementedError

    def get_penalty(self):
        match self.type:
            # Not considered
            case DateType.AS_SOON_AS_POSSIBLE:
                penalty = self.assignment.start - self.day
            case DateType.AS_LATE_AS_POSSIBLE:
                penalty = self.day - self.assignment.end
            # ================================
            case DateType.MUST_START_ON:
                penalty = abs(self.assignment.start - self.day)
            case DateType.MUST_FINISH_ON:
                penalty = abs(self.day - self.assignment.end)
            case DateType.START_NO_EARLIER_THAN:
                penalty = self.day - self.assignment.start
            case DateType.START_NO_LATER_THAN:
                penalty = self.assignment.start - self.day
            case DateType.FINISH_NO_EARLIER_THAN:
                penalty = self.day - self.assignment.end
            case DateType.FINISH_NO_LATER_THAN:
                penalty = self.assignment.end - self.day
            case _:
                raise NotImplementedError

        if penalty < 0:
            return 0

        return penalty

    def get_assignments(self):
        return [self.assignment]

    def attempt_repair(self):
        match self.type:
            case DateType.AS_SOON_AS_POSSIBLE:
                if self.assignment.start > self.day:
                    self.assignment.start = self.day
                    return True
            case DateType.AS_LATE_AS_POSSIBLE:
                if self.assignment.end < self.day:
                    self.assignment.end = self.day
                    return True
            case DateType.MUST_START_ON:
                if self.assignment.start != self.day:
                    self.assignment.start = self.day
                    return True
            case DateType.MUST_FINISH_ON:
                if self.assignment.end != self.day:
                    self.assignment.end = self.day
                    return True
            case DateType.START_NO_EARLIER_THAN:
                if self.assignment.start < self.day:
                    self.assignment.start = self.day
                    return True
            case DateType.START_NO_LATER_THAN:
                if self.assignment.start > self.day:
                    self.assignment.start = self.day
                    return True
            case DateType.FINISH_NO_EARLIER_THAN:
                if self.assignment.end < self.day:
                    self.assignment.end = self.day
                    return True
            case DateType.FINISH_NO_LATER_THAN:
                if self.assignment.end > self.day:
                    self.assignment.end = self.day
                    return True
            case _:
                raise NotImplementedError

        return False

    def is_empty(self) -> bool:
        if self.assignment is None:
            return True

        return False

    def is_start_or_end(self):
        match self.type:
            case (
                DateType.AS_SOON_AS_POSSIBLE
                | DateType.MUST_START_ON
                | DateType.START_NO_EARLIER_THAN
                | DateType.START_NO_LATER_THAN
            ):
                return "start"
            case (
                DateType.AS_LATE_AS_POSSIBLE
                | DateType.MUST_FINISH_ON
                | DateType.FINISH_NO_EARLIER_THAN
                | DateType.FINISH_NO_LATER_THAN
            ):
                return "end"
            case _:
                raise NotImplementedError

    def visualize_gantt(self, ax: Axes):
        # don't draw constraint if it is outside of the plot
        xlim = ax.get_xlim()
        if not (xlim[0] <= self.day <= xlim[1]):
            return ax

        # draw constraint
        match self.type:
            case DateType.AS_SOON_AS_POSSIBLE | DateType.AS_LATE_AS_POSSIBLE:
                x = self.get_constraint_day()
            case _:
                x = self.day

        _, upper = ax.get_ylim()

        penalty = self.get_penalty()

        ax.axvline(
            x,
            ymin=self.assignment.id / upper,
            ymax=(self.assignment.id + 1) / upper,
            color="g" if penalty <= 0 else "r",
            linestyle="--",
            zorder=3,
        )
        ax.text(
            x + 0.15,
            self.assignment.id + 0.75,
            self.type.short_name,
            ha="left",
            va="center",
            color="g" if penalty <= 0 else "r",
            fontsize=8,
            zorder=4,
        )

        return ax

    def to_csv_row(self):
        return ",".join(str(v) for v in [self.assignment.id, self.type.value, self.day])


@dataclass
class ResourceConstraint(BaseConstraint):
    resource: Resource
    assignments: list[Assignment] = field(default_factory=list)
    color: tuple[float] = field(init=False)

    def get_daily_required_capacity(self):
        # construct dict with required capacity per day
        daily_required_capacity: defaultdict[int, float] = defaultdict(float)

        for assignment in self.assignments:
            hours = assignment.hours_per_day
            for day in range(assignment.start, assignment.end):
                daily_required_capacity[day] += hours

        return daily_required_capacity

    def get_penalty(self):
        # skip daily capacity check if total capacity is not exceeded
        if (
            sum(a.hours_per_day for a in self.assignments)
            <= self.resource.total_capacity
        ):
            return 0

        daily_required_capacity = self.get_daily_required_capacity()

        return sum(
            capacity - self.resource.total_capacity
            for capacity in daily_required_capacity.values()
            if capacity > self.resource.total_capacity
        )

    def get_assignments(self):
        return self.assignments

    def _repair_min_duration(self):
        corrected = False

        if self.get_penalty() > 0:
            for assignment in self.assignments:
                if assignment.hours_per_day > self.resource.total_capacity:
                    assignment.duration = math.ceil(
                        assignment.hours / self.resource.total_capacity
                    )
                    corrected = True

        return corrected

    def attempt_repair(self):
        if self._repair_min_duration():
            return True

        return False

    def is_empty(self) -> bool:
        if len(self.assignments) == 0:
            return True

        return False

    def visualize_gantt(self, ax: Axes):
        for assignment in self.assignments:
            ax.add_patch(
                patches.Rectangle(
                    (assignment.start, assignment.id),
                    assignment.duration,
                    1,
                    linewidth=1,
                    zorder=1,
                    facecolor=self.color,
                )
            )

            penalty = self.get_penalty()

            if penalty > 0:
                for day, capacity in self.get_daily_required_capacity().items():
                    if (capacity > self.resource.total_capacity) and (
                        assignment.start <= day < assignment.end
                    ):
                        ax.add_patch(
                            patches.Rectangle(
                                (day, assignment.id),
                                1,
                                0.1,
                                color="r",
                                alpha=0.8,
                                linewidth=0,
                                zorder=2,
                            )
                        )

        return ax

    def to_csv_row(self):
        assignments = ";".join(str(a.id) for a in self.assignments)
        return ",".join(str(v) for v in [self.resource.name, assignments])

    @staticmethod
    def from_csv_row(
        row: dict[str, str], assignments: list[Assignment], resources: list[Resource]
    ):
        assignments = [
            a
            for a in assignments
            if a.id in [int(a_id) for a_id in row["assignment_ids"].split(";")]
        ]
        resource = next(r for r in resources if r.name == row["resource_name"])
        return ResourceConstraint(resource=resource, assignments=assignments)
