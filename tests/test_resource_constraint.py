import pytest

from eaplanner.entities.assignment import Assignment
from eaplanner.entities.constraint import ResourceConstraint
from eaplanner.entities.resource import Resource


def test_daily_required_capacity():
    # arrange
    resource = Resource(
        name="resource",
        min_capacity=10,
        min_cost=1,
        med_capacity=5,
        med_cost=2,
    )
    assignment1 = Assignment(hours=20).set(start=1, duration=2)
    assignment2 = Assignment(hours=20).set(start=2, duration=2)
    resource_constraint = ResourceConstraint(
        resource=resource, assignments=[assignment1, assignment2]
    )

    # act
    result = resource_constraint.get_daily_required_capacity()

    # assert
    assert result[0] == 0
    assert result[1] == 10
    assert result[2] == 20
    assert result[3] == 10
    assert result[4] == 0
    assert sum(result.values()) == 40


def test_resource_penalty():
    # arrange
    resource = Resource(
        name="resource",
        min_capacity=10,
        min_cost=1,
        med_capacity=5,
        med_cost=2,
    )
    assignment1 = Assignment(hours=20).set(start=1, duration=2)
    assignment2 = Assignment(hours=20).set(start=2, duration=2)

    # act
    resource_constraint = ResourceConstraint(
        resource=resource, assignments=[assignment1, assignment2]
    )

    # assert
    assert resource_constraint.get_penalty() == 5
