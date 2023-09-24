use crate::entities::{
    assignment::Assignment,
    constraint::{BaseConstraint, ResourceConstraint},
    resource::Resource,
};

#[test]
fn test_daily_required_capacity() {
    // arrange
    let resource = Resource::new("resource".to_string(), 15);
    let assignment1 = Assignment::new(None, 20);
    assignment1.set_start(1);
    assignment1.set_duration(2);
    let assignment2 = Assignment::new(None, 20);
    assignment2.set_start(2);
    assignment2.set_duration(2);
    let mut resource_constraint = ResourceConstraint::new(resource.clone());
    resource_constraint.add_assignment(assignment1.clone());
    resource_constraint.add_assignment(assignment2.clone());

    // act
    let daily_required_capacity = resource_constraint.get_daily_required_capacity();

    // assert
    assert_eq!(daily_required_capacity[&1], 10);
    assert_eq!(daily_required_capacity[&2], 20);
    assert_eq!(daily_required_capacity[&3], 10);
    assert_eq!(daily_required_capacity.values().sum::<i32>(), 40);
}

#[test]
fn test_resource_penalty() {
    // arrange
    let resource = Resource::new("resource".to_string(), 15);

    let assignment1 = Assignment::new(None, 20);
    assignment1.set_start(1);
    assignment1.set_duration(2);
    let assignment2 = Assignment::new(None, 20);
    assignment2.set_start(2);
    assignment2.set_duration(2);

    // act
    let mut resource_constraint = ResourceConstraint::new(resource.clone());
    resource_constraint.add_assignment(assignment1.clone());
    resource_constraint.add_assignment(assignment2.clone());

    // assert
    assert_eq!(resource_constraint.get_penalty(), 5);
}
