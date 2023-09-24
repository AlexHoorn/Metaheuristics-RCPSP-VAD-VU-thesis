use crate::{algorithms::tools::individual::Individual, entities::schedule::Schedule};

pub trait Interpreter {
    fn interpret(&mut self, chromosome: &Vec<f32>);
    fn evaluate(&mut self, individual: &Individual, repair_pct: f32) -> Vec<i32>;
    fn get_chromosome(&self) -> Vec<f32>;
    fn get_scores(&self) -> Vec<i32>;
    fn get_schedule(&self) -> &Schedule;
}

pub struct AbsoluteScheduleInterpreter {
    pub schedule: Schedule,
}

impl Interpreter for AbsoluteScheduleInterpreter {
    fn interpret(&mut self, chromosome: &Vec<f32>) {
        for i in 0..self.schedule.assignments.len() {
            let assignment = &mut self.schedule.assignments[i];
            assignment.set_start(chromosome[i * 2].round() as i32);
            assignment.set_duration(chromosome[i * 2 + 1].round() as i32);
        }
    }

    fn evaluate(&mut self, individual: &Individual, repair_pct: f32) -> Vec<i32> {
        self.interpret(&individual.chromosome);

        if repair_pct > 0.0 {
            self.schedule.repair_constraints(repair_pct, 1, true);
        }

        self.get_scores()
    }

    fn get_chromosome(&self) -> Vec<f32> {
        let mut chromosome = Vec::new();
        for assignment in self.schedule.assignments.iter() {
            chromosome.push(assignment.start() as f32);
            chromosome.push(assignment.duration() as f32);
        }

        chromosome
    }

    fn get_scores(&self) -> Vec<i32> {
        vec![
            self.schedule.get_total_penalty(),
            self.schedule.get_total_makespan(),
        ]
    }

    fn get_schedule(&self) -> &Schedule {
        &self.schedule
    }
}

impl AbsoluteScheduleInterpreter {
    pub fn new(schedule: Schedule) -> Self {
        Self { schedule }
    }
}
