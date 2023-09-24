use crate::entities::{
    assignment::Assignment,
    constraint::{BaseConstraint, RelationConstraint},
    enum_::RelationType,
};

#[test]
fn test_finish_to_finish() {
    // arrange
    let root_assignment = Assignment::new(None, 10);
    root_assignment.set_start(2);
    root_assignment.set_duration(1);
    let later_assignment = Assignment::new(None, 10);
    later_assignment.set_start(4);
    later_assignment.set_duration(1);
    let ealier_assignment = Assignment::new(None, 10);
    ealier_assignment.set_start(0);
    ealier_assignment.set_duration(1);

    // act
    let relation_later = RelationConstraint::new(
        RelationType::FinishToFinish,
        root_assignment.clone(),
        later_assignment.clone(),
    );
    let relation_earlier = RelationConstraint::new(
        RelationType::FinishToFinish,
        root_assignment.clone(),
        ealier_assignment.clone(),
    );

    // assert
    assert_eq!(relation_later.get_penalty(), 0);
    assert_eq!(relation_earlier.get_penalty(), 2);
}

#[test]
fn test_finish_to_start() {
    // arrange
    let root_assignment = Assignment::new(None, 10);
    root_assignment.set_start(2);
    root_assignment.set_duration(1);
    let later_assignment = Assignment::new(None, 10);
    later_assignment.set_start(4);
    later_assignment.set_duration(1);
    let ealier_assignment = Assignment::new(None, 10);
    ealier_assignment.set_start(0);
    ealier_assignment.set_duration(1);

    // act
    let relation_later = RelationConstraint::new(
        RelationType::FinishToStart,
        root_assignment.clone(),
        later_assignment.clone(),
    );
    let relation_earlier = RelationConstraint::new(
        RelationType::FinishToStart,
        root_assignment.clone(),
        ealier_assignment.clone(),
    );

    // assert
    assert_eq!(relation_later.get_penalty(), 0);
    assert_eq!(relation_earlier.get_penalty(), 3);
}

#[test]
fn test_start_to_finish() {
    // arrange
    let root_assignment = Assignment::new(None, 10);
    root_assignment.set_start(2);
    root_assignment.set_duration(1);
    let later_assignment = Assignment::new(None, 10);
    later_assignment.set_start(4);
    later_assignment.set_duration(1);
    let ealier_assignment = Assignment::new(None, 10);
    ealier_assignment.set_start(0);
    ealier_assignment.set_duration(1);

    // act
    let relation_later = RelationConstraint::new(
        RelationType::StartToFinish,
        root_assignment.clone(),
        later_assignment.clone(),
    );
    let relation_earlier = RelationConstraint::new(
        RelationType::StartToFinish,
        root_assignment.clone(),
        ealier_assignment.clone(),
    );

    // assert
    assert_eq!(relation_later.get_penalty(), 3);
    assert_eq!(relation_earlier.get_penalty(), 0);
}

#[test]
fn test_start_to_start() {
    // arrange
    let root_assignment = Assignment::new(None, 10);
    root_assignment.set_start(2);
    root_assignment.set_duration(1);
    let later_assignment = Assignment::new(None, 10);
    later_assignment.set_start(4);
    later_assignment.set_duration(1);
    let ealier_assignment = Assignment::new(None, 10);
    ealier_assignment.set_start(0);
    ealier_assignment.set_duration(1);

    // act
    let relation_later = RelationConstraint::new(
        RelationType::StartToStart,
        root_assignment.clone(),
        later_assignment.clone(),
    );
    let relation_earlier = RelationConstraint::new(
        RelationType::StartToStart,
        root_assignment.clone(),
        ealier_assignment.clone(),
    );

    // assert
    assert_eq!(relation_later.get_penalty(), 0);
    assert_eq!(relation_earlier.get_penalty(), 2);
}
