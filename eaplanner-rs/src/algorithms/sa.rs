use rand::Rng;

use crate::interpreter::Interpreter;

use super::{
    base::{Algorithm, AlgorithmBase},
    tools::{individual::Individual, utils::is_smaller_or_equal_lexicographic, variation::mutate},
};

pub struct SimulatedAnnealing {
    base: AlgorithmBase,
    mut_indpb: f32,
    mut_mu: f32,
    mut_sigma: f32,
    temperature: f32,
    cooling_rate: f32,
}

impl SimulatedAnnealing {
    pub fn new(
        mu: i32,
        mut_indpb: f32,
        mut_mu: f32,
        mut_sigma: f32,
        temperature: f32,
        cooling_rate: f32,
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
                "SimulatedAnnealing".to_string(),
            ),
            mut_indpb,
            mut_mu,
            mut_sigma,
            temperature,
            cooling_rate,
        }
    }

    pub fn create_offspring(&self, population: &Vec<Individual>) -> Vec<Individual> {
        let mut offspring = Vec::new();

        for ind in population.iter() {
            let child = mutate(ind, self.mut_indpb, self.mut_mu, self.mut_sigma);
            offspring.push(child);
        }

        offspring
    }

    fn transition_probability(
        &self,
        fitness_old: &Vec<i32>,
        fitness_new: &Vec<i32>,
        temp: f32,
    ) -> f32 {
        let delta = fitness_old
            .iter()
            .zip(fitness_new.iter())
            .map(|(a, b)| -(a - b))
            .sum::<i32>();

        (-delta as f32 / temp).exp()
    }
}

impl Algorithm for SimulatedAnnealing {
    fn run(&mut self) {
        let mut generation = 1;
        let mut temp = self.temperature.clone();
        let (mut population, mut evaluations) = self.base().run_start();
        let mut rng = rand::thread_rng();

        while evaluations < self.base().max_evaluations {
            let mut offspring = self.create_offspring(&population);
            evaluations += self.base().evaluate(&mut offspring);

            for i in 0..population.len() {
                if is_smaller_or_equal_lexicographic(
                    offspring[i].fitness.as_ref().unwrap(),
                    population[i].fitness.as_ref().unwrap(),
                ) {
                    population[i] = offspring[i].clone();
                } else if rng.gen::<f32>()
                    < self.transition_probability(
                        population[i].fitness.as_ref().unwrap(),
                        offspring[i].fitness.as_ref().unwrap(),
                        temp,
                    )
                {
                    population[i] = offspring[i].clone();
                }
            }

            self.base()
                .update_logbook(generation, evaluations, &population);
            self.base().save_population(&population, generation);
            self.base().hall_of_fame.update(&population);
            temp *= self.cooling_rate;
            generation += 1;
        }

        self.base.run_finish();
    }

    fn base(&mut self) -> &mut AlgorithmBase {
        &mut self.base
    }
}
