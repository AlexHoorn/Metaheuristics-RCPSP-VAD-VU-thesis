use std::any::Any;
use std::vec::Vec;
use std::{collections::HashMap, rc::Rc};

use super::{assignment::Assignment, enum_::RelationType, resource::Resource};

pub trait BaseConstraint {
    fn get_penalty(&self) -> i32;
    fn attempt_repair(&self) -> bool;
    fn as_any(&self) -> &dyn Any;
    fn get_name(&self) -> String;
}

#[derive(Debug, Clone)]
pub struct RelationConstraint {
    pub r#type: RelationType,
    pub predecessor: Rc<Assignment>,
    pub successor: Rc<Assignment>,
}

impl BaseConstraint for RelationConstraint {
    fn get_penalty(&self) -> i32 {
        let penalty = match self.r#type {
            RelationType::FinishToFinish => self.predecessor.end() - self.successor.end(),
            RelationType::FinishToStart => self.predecessor.end() - self.successor.start(),
            RelationType::StartToFinish => self.successor.end() - self.predecessor.start(),
            RelationType::StartToStart => self.predecessor.start() - self.successor.start(),
        };

        if penalty <= 0 {
            return 0;
        }

        penalty
    }

    fn attempt_repair(&self) -> bool {
        match self.r#type {
            RelationType::FinishToFinish => {
                if self.predecessor.end() > self.successor.end() {
                    self.successor.set_end(self.predecessor.end());
                    return true;
                }
            }
            RelationType::FinishToStart => {
                if self.predecessor.end() > self.successor.start() {
                    self.successor.set_start(self.predecessor.end());
                    return true;
                }
            }
            RelationType::StartToFinish => {
                if self.successor.end() > self.predecessor.start() {
                    self.successor.set_end(self.predecessor.start());
                    return true;
                }
            }
            RelationType::StartToStart => {
                if self.predecessor.start() > self.successor.start() {
                    self.successor.set_start(self.predecessor.start());
                    return true;
                }
            }
        }

        false
    }

    fn as_any(&self) -> &dyn Any {
        self
    }

    fn get_name(&self) -> String {
        "RelationConstraint".to_string()
    }
}

impl RelationConstraint {
    pub fn new(
        r#type: RelationType,
        predecessor: Rc<Assignment>,
        successor: Rc<Assignment>,
    ) -> Self {
        Self {
            r#type,
            predecessor,
            successor,
        }
    }

    pub fn set_predecessor(&mut self, predecessor: Rc<Assignment>) {
        self.predecessor = predecessor;
    }

    pub fn set_successor(&mut self, successor: Rc<Assignment>) {
        self.successor = successor;
    }
}

#[derive(Debug, Clone)]
pub struct ResourceConstraint {
    pub resource: Rc<Resource>,
    pub assignments: Vec<Rc<Assignment>>,
}

impl BaseConstraint for ResourceConstraint {
    fn get_penalty(&self) -> i32 {
        let daily_required_capacity = self.get_daily_required_capacity();

        let penalty = daily_required_capacity
            .values()
            .filter(|&capacity| capacity > &self.resource.capacity())
            .map(|capacity| capacity - &self.resource.capacity())
            .sum();

        penalty
    }

    fn attempt_repair(&self) -> bool {
        let mut corrected = false;

        if self.get_penalty() > 0 {
            for assignment in self.assignments.iter() {
                if assignment.hours_per_day() > self.resource.capacity() {
                    let duration =
                        (assignment.hours() as f32 / self.resource.capacity() as f32).ceil() as i32;
                    assignment.set_duration(duration);
                    corrected = true;
                }
            }
        }

        return corrected;
    }

    fn as_any(&self) -> &dyn Any {
        self
    }

    fn get_name(&self) -> String {
        "ResourceConstraint".to_string()
    }
}

impl ResourceConstraint {
    pub fn new(resource: Rc<Resource>) -> Self {
        Self {
            resource,
            assignments: Vec::new(),
        }
    }

    pub fn add_assignment(&mut self, assignment: Rc<Assignment>) {
        self.assignments.push(assignment);
    }

    pub fn get_daily_required_capacity(&self) -> HashMap<i32, i32> {
        let mut daily_required_capacity = HashMap::new();

        for assignment in &self.assignments {
            let hours = assignment.hours_per_day();
            for day in assignment.start()..assignment.end() {
                *daily_required_capacity.entry(day).or_insert(0) += hours;
            }
        }

        daily_required_capacity
    }
}
