use crate::entities::{
    assignment::Assignment, constraint::RelationConstraint, enum_::RelationType, schedule::Schedule,
};

#[test]
fn test_schedule_total_duration() {
    // arrange
    let assignment1 = Assignment::new(None, 10);
    assignment1.set_start(0);
    assignment1.set_duration(1);
    let assignment2 = Assignment::new(None, 10);
    assignment2.set_start(9);
    assignment2.set_duration(1);
    let assignment3 = Assignment::new(None, 10);
    assignment3.set_start(3);
    assignment3.set_duration(1);

    // act
    let mut schedule = Schedule::new();
    schedule.add_assignments(vec![assignment1, assignment2, assignment3]);

    // assert
    assert_eq!(schedule.get_total_makespan(), 10);
    assert_eq!(schedule.get_total_penalty(), 0);
}

#[test]
fn test_schedule_total_duration_empty() {
    // arrange
    let schedule = Schedule::new();

    // assert
    assert_eq!(schedule.get_total_makespan(), 0);
}

#[test]
fn test_schedule_total_duration_negative() {
    // arrange
    let assignment1 = Assignment::new(None, 10);
    assignment1.set_start(0);
    assignment1.set_duration(1);
    let assignment2 = Assignment::new(None, 10);
    assignment2.set_start(-1);
    assignment2.set_duration(-1);
    let assignment3 = Assignment::new(None, 10);
    assignment3.set_start(3);
    assignment3.set_duration(1);
    let relation_constraint = RelationConstraint::new(
        RelationType::FinishToStart,
        assignment1.clone(),
        assignment2.clone(),
    );

    // act
    let mut schedule = Schedule::new();
    schedule.add_assignments(vec![assignment1, assignment2, assignment3]);
    schedule.add_constraint(Box::new(relation_constraint));

    // assert
    assert_eq!(schedule.get_total_makespan(), 5);
    assert_eq!(schedule.get_total_penalty(), 2);
}
