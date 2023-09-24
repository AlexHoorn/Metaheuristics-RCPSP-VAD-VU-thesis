from eaplanner.entities.enum import RelationType
from eaplanner.entities.schedule import Assignment, Schedule
from eaplanner.entities.constraint import RelationConstraint


def test_schedule_total_duration():
    # arrange
    assignments = [
        Assignment().set(start=0, duration=1),
        Assignment().set(start=9, duration=1),
        Assignment().set(start=3, duration=1),
    ]

    # act
    schedule = Schedule(assignments)

    # assert
    assert schedule.get_total_makespan() == 10
    assert schedule.get_total_penalty() == 0


def test_schedule_total_duration_empty():
    # arrange
    assignments = []

    # act
    schedule = Schedule(assignments)

    # assert
    assert schedule.get_total_makespan() == 0


def test_schedule_total_duration_negative():
    # arrange
    assignments = [
        Assignment().set(start=0, duration=1),
        Assignment().set(start=-1, duration=-1),
        Assignment().set(start=3, duration=1),
    ]
    relation = RelationConstraint(
        type=RelationType.FINISH_TO_START,
        predecessor=assignments[0],
        successor=assignments[1],
    )

    # act
    schedule = Schedule(assignments)
    schedule.add_constraint(relation)

    # assert
    assert schedule.get_total_makespan() == 5
    assert schedule.get_total_penalty() == 2


def test_schedule_total_duration_negative_empty():
    # arrange
    assignments = [
        Assignment().set(start=-1, duration=-1),
    ]

    # act
    schedule = Schedule(assignments)

    # assert
    assert schedule.get_total_makespan() == 1
    assert schedule.get_total_penalty() == 0


def test_schedule_total_penalty():
    # arrange
    assignments = [
        Assignment().set(start=0, duration=1),
        Assignment().set(start=9, duration=1),
        Assignment().set(start=3, duration=1),
    ]
    relations = [
        RelationConstraint(
            type=RelationType.FINISH_TO_START,
            predecessor=assignments[0],
            successor=assignments[1],
        ),
        RelationConstraint(
            type=RelationType.FINISH_TO_START,
            predecessor=assignments[1],
            successor=assignments[2],
        ),
    ]

    # act
    schedule = Schedule(assignments, relations)

    # assert
    assert schedule.get_total_makespan() == 10
    assert schedule.get_total_penalty() == 7


def test_schedule_total_penalty_empty():
    # arrange
    assignments = [
        Assignment().set(start=0, duration=1),
        Assignment().set(start=9, duration=1),
        Assignment().set(start=3, duration=1),
    ]

    # act
    schedule = Schedule(assignments)

    # assert
    assert schedule.get_total_makespan() == 10
    assert schedule.get_total_penalty() == 0
