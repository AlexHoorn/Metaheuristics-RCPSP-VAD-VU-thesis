from eaplanner.entities.assignment import Assignment
from eaplanner.entities.constraint import DateConstraint
from eaplanner.entities.enum import DateType


def test_as_soon_as_possible():
    # arrange
    assignment = Assignment().set(start=2, duration=1)

    # act
    date_later = DateConstraint(
        type=DateType.AS_SOON_AS_POSSIBLE,
        assignment=assignment,
        day=4,
    )
    date_earlier = DateConstraint(
        type=DateType.AS_SOON_AS_POSSIBLE,
        assignment=assignment,
        day=0,
    )

    # assert
    assert date_later.get_penalty() == 0
    assert date_earlier.get_penalty() == 2


def test_as_late_as_possible():
    # arrange
    assignment = Assignment().set(start=2, duration=1)

    # act
    date_later = DateConstraint(
        type=DateType.AS_LATE_AS_POSSIBLE,
        assignment=assignment,
        day=4,
    )
    date_earlier = DateConstraint(
        type=DateType.AS_LATE_AS_POSSIBLE,
        assignment=assignment,
        day=0,
    )

    # assert
    assert date_later.get_penalty() == 1
    assert date_earlier.get_penalty() == 0


def test_must_start_on():
    # arrange
    assignment = Assignment().set(start=2, duration=1)

    # act
    date_later = DateConstraint(
        type=DateType.MUST_START_ON,
        assignment=assignment,
        day=4,
    )
    date_earlier = DateConstraint(
        type=DateType.MUST_START_ON,
        assignment=assignment,
        day=0,
    )

    # assert
    assert date_later.get_penalty() == 2
    assert date_earlier.get_penalty() == 2


def test_must_finish_on():
    # arrange
    assignment = Assignment().set(start=2, duration=1)

    # act
    date_later = DateConstraint(
        type=DateType.MUST_FINISH_ON,
        assignment=assignment,
        day=4,
    )
    date_earlier = DateConstraint(
        type=DateType.MUST_FINISH_ON,
        assignment=assignment,
        day=0,
    )

    # assert
    assert date_later.get_penalty() == 1
    assert date_earlier.get_penalty() == 3


def test_start_no_earlier_than():
    # arrange
    assignment = Assignment().set(start=2, duration=1)

    # act
    date_later = DateConstraint(
        type=DateType.START_NO_EARLIER_THAN,
        assignment=assignment,
        day=4,
    )
    date_earlier = DateConstraint(
        type=DateType.START_NO_EARLIER_THAN,
        assignment=assignment,
        day=0,
    )

    # assert
    assert date_later.get_penalty() == 2
    assert date_earlier.get_penalty() == 0


def test_start_no_later_than():
    # arrange
    assignment = Assignment().set(start=2, duration=1)

    # act
    date_later = DateConstraint(
        type=DateType.START_NO_LATER_THAN,
        assignment=assignment,
        day=4,
    )
    date_earlier = DateConstraint(
        type=DateType.START_NO_LATER_THAN,
        assignment=assignment,
        day=0,
    )

    # assert
    assert date_later.get_penalty() == 0
    assert date_earlier.get_penalty() == 2


def test_finish_no_earlier_than():
    # arrange
    assignment = Assignment().set(start=2, duration=1)

    # act
    date_later = DateConstraint(
        type=DateType.FINISH_NO_EARLIER_THAN,
        assignment=assignment,
        day=4,
    )
    date_earlier = DateConstraint(
        type=DateType.FINISH_NO_EARLIER_THAN,
        assignment=assignment,
        day=0,
    )

    # assert
    assert date_later.get_penalty() == 1
    assert date_earlier.get_penalty() == 0


def test_finish_no_later_than():
    # arrange
    assignment = Assignment().set(start=2, duration=1)

    # act
    date_later = DateConstraint(
        type=DateType.FINISH_NO_LATER_THAN,
        assignment=assignment,
        day=4,
    )
    date_earlier = DateConstraint(
        type=DateType.FINISH_NO_LATER_THAN,
        assignment=assignment,
        day=0,
    )

    # assert
    assert date_later.get_penalty() == 0
    assert date_earlier.get_penalty() == 3
