use rand::seq::SliceRandom;
use rand::Rng;
use std::path::Path;
use std::rc::Rc;

use super::assignment::Assignment;
use super::constraint::{BaseConstraint, RelationConstraint, ResourceConstraint};
use super::resource::Resource;
// use rand::prelude::*;

pub struct Schedule {
    pub assignments: Vec<Rc<Assignment>>,
    pub constraints: Vec<Box<dyn BaseConstraint>>,
}

impl Schedule {
    pub fn new() -> Self {
        Self {
            assignments: Vec::new(),
            constraints: Vec::new(),
        }
    }

    pub fn add_assignments(&mut self, assignments: Vec<Rc<Assignment>>) {
        for assignment in assignments {
            self.add_assignment(assignment);
        }
    }

    pub fn add_assignment(&mut self, assignment: Rc<Assignment>) {
        self.assignments.push(assignment);
    }

    pub fn add_constraints(&mut self, constraints: Vec<Box<dyn BaseConstraint>>) {
        for constraint in constraints {
            self.add_constraint(constraint);
        }
    }

    pub fn add_constraint(&mut self, constraint: Box<dyn BaseConstraint>) {
        self.constraints.push(constraint);
    }

    pub fn get_total_makespan(&self) -> i32 {
        self.get_end() - self.get_start()
    }

    pub fn get_start(&self) -> i32 {
        self.assignments
            .iter()
            .map(|a| a.start())
            .min()
            .unwrap_or_default()
    }

    pub fn get_end(&self) -> i32 {
        self.assignments
            .iter()
            .map(|a| a.end())
            .max()
            .unwrap_or_default()
    }

    pub fn get_total_penalty(&self) -> i32 {
        self.constraints
            .iter()
            .map(|c| c.get_penalty())
            .sum::<i32>()
    }

    pub fn repair_constraints(&self, pct: f32, max_loops: i32, shuffle: bool) {
        let mut rng = rand::thread_rng();
        let mut corrected = false;

        let mut order: Vec<usize> = (0..self.constraints.len()).collect();

        for _ in 0..max_loops {
            if shuffle {
                order.shuffle(&mut rng);
            }

            for i in order.iter() {
                if rng.gen::<f32>() < pct {
                    // false | false = false
                    corrected |= self.constraints[*i].attempt_repair();
                }
            }

            if !corrected {
                break;
            }
        }
    }

    pub fn get_constraints_per_type(&self) -> (Vec<&ResourceConstraint>, Vec<&RelationConstraint>) {
        let mut resource_constraints = Vec::new();
        let mut relation_constraints = Vec::new();

        for constraint in self.constraints.iter() {
            if let Some(resource_constraint) =
                constraint.as_any().downcast_ref::<ResourceConstraint>()
            {
                resource_constraints.push(resource_constraint);
            } else if let Some(relation_constraint) =
                constraint.as_any().downcast_ref::<RelationConstraint>()
            {
                relation_constraints.push(relation_constraint);
            }
        }

        (resource_constraints, relation_constraints)
    }

    pub fn to_csv(&self, save_folder: &Path) {
        // write assignments
        let assignments_filepath = save_folder.join("activities.csv");
        let assignments_file =
            std::fs::File::create(assignments_filepath).expect("Failed to create file");
        let mut assignments_writer = csv::Writer::from_writer(assignments_file);
        assignments_writer
            .write_record(&["id", "hours", "start", "duration"])
            .expect("Failed to write header");

        for assignment in self.assignments.iter() {
            assignments_writer
                .write_record(&[
                    assignment.id().to_string(),
                    assignment.hours().to_string(),
                    assignment.start().to_string(),
                    assignment.duration().to_string(),
                ])
                .expect("Failed to write data");
        }

        // get the different constraints
        let (resource_constraints, relation_constraints) = self.get_constraints_per_type();

        // write resources
        let resources_filepath = save_folder.join("resources.csv");
        let resources_file =
            std::fs::File::create(resources_filepath).expect("Failed to create file");
        let mut resources_writer = csv::Writer::from_writer(resources_file);
        resources_writer
            .write_record(&["name", "total_capacity"])
            .expect("Failed to write header");

        let resources = resource_constraints
            .iter()
            .map(|c| c.resource.clone())
            .collect::<Vec<Rc<Resource>>>();
        let mut unique_resources = Vec::new();
        for resource in resources.iter() {
            if !unique_resources.contains(resource) {
                unique_resources.push(resource.clone());
            }
        }
        for resource in unique_resources.iter() {
            resources_writer
                .write_record(&[resource.name().to_string(), resource.capacity().to_string()])
                .expect("Failed to write data");
        }

        // write relation constraints
        let relations_filepath = save_folder.join("sequence_constraints.csv");
        let relations_file =
            std::fs::File::create(relations_filepath).expect("Failed to create file");
        let mut relations_writer = csv::Writer::from_writer(relations_file);
        relations_writer
            .write_record(&["predecessor_id", "successor_id", "type"])
            .expect("Failed to write header");

        for constraint in relation_constraints.iter() {
            relations_writer
                .write_record(&[
                    constraint.predecessor.id().to_string(),
                    constraint.successor.id().to_string(),
                    (constraint.r#type as u8).to_string(),
                ])
                .expect("Failed to write data");
        }

        // write resource constraints
        let resource_constraints_filepath = save_folder.join("resource_constraints.csv");
        let resource_constraints_file =
            std::fs::File::create(resource_constraints_filepath).expect("Failed to create file");
        let mut resource_constraints_writer = csv::Writer::from_writer(resource_constraints_file);
        resource_constraints_writer
            .write_record(&["resource_name", "assignment_ids"])
            .expect("Failed to write header");

        for constraint in resource_constraints.iter() {
            let assignments = constraint
                .assignments
                .iter()
                .map(|f| f.id().to_string())
                .collect::<Vec<String>>()
                .join(";");
            resource_constraints_writer
                .write_record(&[constraint.resource.name(), assignments])
                .expect("Failed to write data");
        }
    }
}
