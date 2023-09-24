use crate::algorithms::tools::individual::Individual;
use crate::algorithms::tools::utils::is_smaller_or_equal_lexicographic;
use crate::interpreter::Interpreter;

use super::base::{Algorithm, AlgorithmBase};

pub struct FixerOnly {
    base: AlgorithmBase,
}

impl FixerOnly {
    pub fn new(
        mu: i32,
        repair_pct: f32,
        max_evaluations: i32,
        pmin: i32,
        pmax: i32,
        interpreter: Box<dyn Interpreter>,
        verbose: bool,
        save_population: bool,
        save_folder: String,
    ) -> Self {
        Self {
            base: AlgorithmBase::new(
                mu,
                repair_pct,
                max_evaluations,
                pmin,
                pmax,
                interpreter,
                verbose,
                save_population,
                save_folder,
                "FixerOnly".to_string(),
            ),
        }
    }

    pub fn create_offspring(&self, population: &Vec<Individual>) -> Vec<Individual> {
        let mut offspring = Vec::new();

        for ind in population.iter() {
            let mut child = ind.clone();
            child.fitness = None;
            offspring.push(child);
        }

        offspring
    }
}

impl Algorithm for FixerOnly {
    fn run(&mut self) {
        let mut generation = 1;
        let (mut population, mut evaluations) = self.base.run_start();

        while evaluations < self.base.max_evaluations {
            let mut offspring = self.create_offspring(&population);
            evaluations += self.base.evaluate(&mut offspring);

            for i in 0..population.len() {
                if is_smaller_or_equal_lexicographic(
                    offspring[i].fitness.as_ref().unwrap(),
                    population[i].fitness.as_ref().unwrap(),
                ) {
                    population[i] = offspring[i].clone();
                }
            }

            self.base
                .update_logbook(generation, evaluations, &population);
            self.base.save_population(&population, generation);
            self.base.hall_of_fame.update(&population);
            generation += 1;
        }

        self.base.run_finish();
    }

    fn base(&mut self) -> &mut AlgorithmBase {
        &mut self.base
    }
}
