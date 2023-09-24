from eaplanner.interpreter import AbsoluteScheduleInterpreter

from eaplanner.entities.schedule import Schedule
from eaplanner.entities.assignment import Assignment
import numpy as np


def test_absolute_interpret():
    # arrange
    assignments = [
        Assignment(),
        Assignment(),
        Assignment(),
    ]
    schedule = Schedule(assignments)
    interpreter = AbsoluteScheduleInterpreter(schedule)
    chromosome = np.array([0, 1, 9, 1, 3, 1])

    # act
    interpreter.interpret(chromosome)

    # assert
    assert assignments[0].start == 0
    assert assignments[0].duration == 1
    assert assignments[1].start == 9
    assert assignments[1].duration == 1
    assert assignments[2].start == 3
    assert assignments[2].duration == 1
    assert schedule.get_total_makespan() == 10
    assert schedule.get_total_penalty() == 0
