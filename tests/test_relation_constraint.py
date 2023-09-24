from eaplanner.entities.enum import RelationType
from eaplanner.entities.schedule import Assignment
from eaplanner.entities.constraint import RelationConstraint


def test_finish_to_finish():
    # arrange
    root_assignment = Assignment().set(start=2, duration=1)
    later_assignment = Assignment().set(start=4, duration=1)
    earlier_assignment = Assignment().set(start=0, duration=1)

    # act
    relation_later = RelationConstraint(
        type=RelationType.FINISH_TO_FINISH,
        predecessor=root_assignment,
        successor=later_assignment,
    )
    relation_earlier = RelationConstraint(
        type=RelationType.FINISH_TO_FINISH,
        predecessor=root_assignment,
        successor=earlier_assignment,
    )

    # assert
    assert relation_later.get_penalty() == 0
    assert relation_earlier.get_penalty() == 2


def test_finish_to_start():
    # arrange
    root_assignment = Assignment().set(start=2, duration=1)
    later_assignment = Assignment().set(start=4, duration=1)
    earlier_assignment = Assignment().set(start=0, duration=1)

    # act
    relation_later = RelationConstraint(
        type=RelationType.FINISH_TO_START,
        predecessor=root_assignment,
        successor=later_assignment,
    )
    relation_earlier = RelationConstraint(
        type=RelationType.FINISH_TO_START,
        predecessor=root_assignment,
        successor=earlier_assignment,
    )

    # assert
    assert relation_later.get_penalty() == 0
    assert relation_earlier.get_penalty() == 3


def test_start_to_finish():
    # arrange
    root_assignment = Assignment().set(start=2, duration=1)
    later_assignment = Assignment().set(start=4, duration=1)
    earlier_assignment = Assignment().set(start=0, duration=1)

    # act
    relation_later = RelationConstraint(
        type=RelationType.START_TO_FINISH,
        predecessor=root_assignment,
        successor=later_assignment,
    )
    relation_earlier = RelationConstraint(
        type=RelationType.START_TO_FINISH,
        predecessor=root_assignment,
        successor=earlier_assignment,
    )

    # assert
    assert relation_later.get_penalty() == 3
    assert relation_earlier.get_penalty() == 0


def test_start_to_start():
    # arrange
    root_assignment = Assignment().set(start=2, duration=1)
    later_assignment = Assignment().set(start=4, duration=1)
    earlier_assignment = Assignment().set(start=0, duration=1)

    # act
    relation_later = RelationConstraint(
        type=RelationType.START_TO_START,
        predecessor=root_assignment,
        successor=later_assignment,
    )
    relation_earlier = RelationConstraint(
        type=RelationType.START_TO_START,
        predecessor=root_assignment,
        successor=earlier_assignment,
    )

    # assert
    assert relation_later.get_penalty() == 0
    assert relation_earlier.get_penalty() == 2
