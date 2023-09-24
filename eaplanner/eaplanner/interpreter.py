import pickle
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from eaplanner.entities.schedule import Schedule

if TYPE_CHECKING:
    from eaplanner.algorithms.base import Individual


@dataclass
class ScheduleInterpreterBase(metaclass=ABCMeta):
    schedule: Schedule
    repair_pct: float = 1.0

    @abstractmethod
    def interpret(self, chromosome: "Individual") -> None:
        raise NotImplementedError

    def interpret_and_get_scores(self, chromosome: "Individual"):
        self.interpret(chromosome)

        if self.repair_pct > 0:
            self.schedule.repair_constraints(max_loops=1, shuffle=True, pct=self.repair_pct)

        return self.get_scores(), self.to_chromosome()

    def get_scores(self):
        return (
            self.schedule.get_total_penalty(),
            self.schedule.get_total_makespan(),
        )

    def to_chromosome(self) -> "Individual":
        chromosome = []
        for assignment in self.schedule.assignments:
            chromosome.append(assignment.start)
            chromosome.append(assignment.duration)

        return np.array(chromosome, dtype=np.float64)

    @property
    def score_names(self):
        return "penalty", "makespan"

    @staticmethod
    def load(filename: Path):
        if not filename.exists():
            raise FileNotFoundError(f"File {filename} does not exist")

        loaded = pickle.loads(filename.read_bytes())

        if not isinstance(loaded, ScheduleInterpreterBase):
            raise ValueError("File does not contain a Schedule object")

        return loaded


# class that translates the chromosome from the evolutionary algorithm into a schedule
# the chromosome is a list of tuples, each tuple represents an assignment
class AbsoluteScheduleInterpreter(ScheduleInterpreterBase):
    # the first element of the tuple is the start date of the assignment
    # the second element of the tuple is the duration of the assignment
    def interpret(self, chromosome: "Individual"):
        chromosome = chromosome.round()

        starts = chromosome[::2]
        durations = chromosome[1::2]

        for assignment, start, duration in zip(
            self.schedule.assignments, starts, durations
        ):
            assignment.start = int(start)
            assignment.duration = int(duration)
