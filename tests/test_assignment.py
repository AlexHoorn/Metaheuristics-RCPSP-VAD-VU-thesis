from eaplanner.entities.schedule import Assignment


def test_assignment_set():
    # arrange
    inplace_assignment = Assignment(hours=10)

    # act
    returned_assignmend = inplace_assignment.set(start=2, duration=1)

    # assert
    assert inplace_assignment.start == 2
    assert inplace_assignment.duration == 1
    assert inplace_assignment.end == 3
    assert inplace_assignment.hours_per_day == 10
    assert returned_assignmend is inplace_assignment


def test_assignment_set_negative():
    # arrange
    assignment = Assignment(hours=10)

    # act
    assignment.set(start=-1, duration=-1)

    # assert
    assert assignment.start == -1
    assert assignment.duration == 1
    assert assignment.end == 0
    assert assignment.hours_per_day == 10
