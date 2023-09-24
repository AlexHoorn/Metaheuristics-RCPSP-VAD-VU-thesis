use crate::entities::assignment::Assignment;

#[test]
fn test_assignment_set() {
    let assignment = Assignment::new(None, 10);

    assignment.set_start(2);
    assignment.set_duration(1);

    assert_eq!(assignment.start(), 2);
    assert_eq!(assignment.duration(), 1);
    assert_eq!(assignment.end(), 3);
    assert_eq!(assignment.hours_per_day(), 10);
}

#[test]
fn test_assignment_set_negative() {
    let assignment = Assignment::new(None, 10);

    assignment.set_start(-1);
    assignment.set_duration(-1);

    assert_eq!(assignment.start(), -1);
    assert_eq!(assignment.duration(), 1);
    assert_eq!(assignment.end(), 0);
    assert_eq!(assignment.hours_per_day(), 10);
}
