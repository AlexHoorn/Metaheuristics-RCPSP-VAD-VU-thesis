use crate::Schedule;
use std::{path::Path, rc::Rc};

use crate::entities::{
    assignment::Assignment,
    constraint::{RelationConstraint, ResourceConstraint},
    enum_::RelationType,
    resource::Resource,
};

fn load_assignments(filepath: &Path) -> Vec<Rc<Assignment>> {
    let mut assignments = Vec::new();
    let filepath = filepath.join("activities.csv");
    let mut rdr = csv::Reader::from_path(filepath).unwrap();

    for result in rdr.records() {
        let record = result.unwrap();
        let id = record[0].parse::<usize>().unwrap();
        let hours = record[1].parse::<i32>().unwrap();
        let start = record[2].parse::<i32>().unwrap();
        let duration = record[3].parse::<i32>().unwrap();
        let assignment = Assignment::new(Some(id), hours);
        assignment.set_start(start);
        assignment.set_duration(duration);
        assignments.push(assignment);
    }
    assignments
}

fn load_resources(filepath: &Path) -> Vec<Rc<Resource>> {
    let mut resources = Vec::new();
    let filepath = filepath.join("resources.csv");
    let mut rdr = csv::Reader::from_path(filepath).unwrap();

    for result in rdr.records() {
        let record = result.unwrap();
        let id = record[0].parse::<String>().unwrap();
        let capacity = record[1].parse::<i32>().unwrap();
        let resource = Resource::new(id, capacity);
        resources.push(resource);
    }
    resources
}

fn load_relation_constraints(
    filepath: &Path,
    assignments: Vec<Rc<Assignment>>,
) -> Vec<RelationConstraint> {
    let mut relation_constraints = Vec::new();
    let filepath = filepath.join("sequence_constraints.csv");
    let mut rdr = csv::Reader::from_path(filepath).unwrap();

    // assignments to hashmap for faster lookup using id
    let mut assignments_map = std::collections::HashMap::new();
    for assignment in assignments.iter() {
        assignments_map.insert(assignment.id(), assignment);
    }

    for result in rdr.records() {
        let record = result.unwrap();
        let predecessor_id = record[0].parse::<usize>().unwrap();
        let successor_id = record[1].parse::<usize>().unwrap();
        let r#type = RelationType::try_from(record[2].parse::<i32>().unwrap()).unwrap();

        let relation_constraint = RelationConstraint::new(
            r#type,
            assignments_map[&predecessor_id].clone(),
            assignments_map[&successor_id].clone(),
        );
        relation_constraints.push(relation_constraint);
    }
    relation_constraints
}

fn load_resource_constraints(
    filepath: &Path,
    resources: Vec<Rc<Resource>>,
    assignments: Vec<Rc<Assignment>>,
) -> Vec<ResourceConstraint> {
    let mut resource_constraints = Vec::new();
    let filepath = filepath.join("resource_constraints.csv");
    let mut rdr = csv::Reader::from_path(filepath).unwrap();

    for result in rdr.records() {
        let record = result.unwrap();
        let resource_id = record[0].parse::<String>().unwrap();
        let assignment_ids: Vec<usize> = record[1]
            .parse::<String>()
            .unwrap()
            .split(";")
            .map(|s| s.parse::<usize>().unwrap())
            .collect();

        let resource = resources.iter().find(|r| r.name() == resource_id).unwrap();
        let resource_assignments = assignments
            .iter()
            .filter(|a| assignment_ids.contains(&a.id()))
            .collect::<Vec<_>>();

        let mut resource_constraint = ResourceConstraint::new(resource.clone());
        for assignment in resource_assignments {
            resource_constraint.add_assignment(assignment.clone());
        }
        resource_constraints.push(resource_constraint);
    }
    resource_constraints
}

pub fn load_schedule(path: &Path) -> Schedule {
    let mut schedule = Schedule::new();

    // load assignments, resources, and constraints
    let assignments = load_assignments(&path);
    let resources = load_resources(&path);

    let relation_constraints = load_relation_constraints(&path, assignments.clone());
    let resource_constraints = load_resource_constraints(&path, resources, assignments.clone());

    for assignment in assignments.iter() {
        schedule.add_assignment(assignment.clone());
    }
    for constraint in relation_constraints.iter() {
        schedule.add_constraint(Box::new(constraint.clone()));
    }
    for constraint in resource_constraints.iter() {
        schedule.add_constraint(Box::new(constraint.clone()));
    }

    schedule
}
