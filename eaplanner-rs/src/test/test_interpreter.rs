use crate::{
    entities::{assignment::Assignment, schedule::Schedule},
    interpreter::{AbsoluteScheduleInterpreter, Interpreter},
};

#[test]
fn test_absolute_interpret() {
    // arrange
    let assignments = vec![
        Assignment::new(None, 10),
        Assignment::new(None, 10),
        Assignment::new(None, 10),
    ];
    let mut schedule = Schedule::new();
    schedule.add_assignments(assignments);
    let mut interpreter = AbsoluteScheduleInterpreter::new(schedule);
    let chromosome = vec![0.0, 1.0, 9.0, 1.0, 3.0, 1.0];

    // act
    interpreter.interpret(&chromosome);

    // assert
    assert_eq!(interpreter.schedule.assignments[0].start(), 0);
    assert_eq!(interpreter.schedule.assignments[0].duration(), 1);
    assert_eq!(interpreter.schedule.assignments[1].start(), 9);
    assert_eq!(interpreter.schedule.assignments[1].duration(), 1);
    assert_eq!(interpreter.schedule.assignments[2].start(), 3);
    assert_eq!(interpreter.schedule.assignments[2].duration(), 1);
    assert_eq!(interpreter.schedule.get_total_makespan(), 10);
    assert_eq!(interpreter.schedule.get_total_penalty(), 0);
}
