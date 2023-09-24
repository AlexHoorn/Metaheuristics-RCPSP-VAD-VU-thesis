use rand::Rng;

use crate::interpreter::Interpreter;

use super::{
    base::{Algorithm, AlgorithmBase},
    tools::{
        individual::Individual,
        variation::{crossover, mutate},
    },
};

pub struct GeneticAlgorithm {
    base: AlgorithmBase,
    lambda: i32,
    cxpb: f32,
    mut_indpb: f32,
    mut_mu: f32,
    mut_sigma: f32,
}

impl Algorithm for GeneticAlgorithm {
    fn run(&mut self) {
        let mut generation = 1;
        let (mut population, mut evaluations) = self.base.run_start();

        while evaluations < self.base.max_evaluations {
            let mut offspring = self.variation(
                &population,
                self.lambda,
                self.cxpb,
                self.mut_indpb,
                self.mut_mu,
                self.mut_sigma,
            );

            let inner_evaluations = self.base.evaluate(&mut offspring);
            evaluations += inner_evaluations;

            // TODO: implement NSGA-III
            population = nsga_selection(
                population
                    .into_iter()
                    .chain(offspring.into_iter())
                    .collect(),
                self.base.mu,
            );

            self.base
                .logbook
                .record(generation, evaluations, &population);
            self.base.save_population(&population, generation);
            self.base.hall_of_fame.update(&population);
        }
    }

    fn base(&mut self) -> &mut AlgorithmBase {
        &mut self.base
    }
}

impl GeneticAlgorithm {
    pub fn new(
        mu: i32,
        lambda: i32,
        cxpb: f32,
        ind_mutpb: f32,
        mut_mu: f32,
        mut_sigma: f32,
        repair_pct: f32,
        max_evaluations: i32,
        pmin: i32,
        pmax: i32,
        interpreter: Box<dyn Interpreter>,
        verbose: bool,
        save: bool,
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
                "GeneticAlgorithm".to_string(),
            ),
            lambda,
            cxpb,
            mut_indpb: ind_mutpb,
            mut_mu,
            mut_sigma,
        }
    }

    fn variation(
        &self,
        population: &Vec<Individual>,
        lambda: i32,
        cxpb: f32,
        ind_mutpb: f32,
        mut_mu: f32,
        mut_sigma: f32,
    ) -> Vec<Individual> {
        let mut offspring = Vec::new();
        let mut index = 0;
        let mut rng = rand::thread_rng();

        for _ in 0..lambda {
            if rng.gen::<f32>() < cxpb {
                let mut parent1 = population[rng.gen_range(0..population.len())];
                let mut parent2 = population[rng.gen_range(0..population.len())];
                let child = crossover(&parent1, &parent2);

                offspring.push(child);
            } else {
                let mut child = population[index % population.len()].clone();
                child = mutate(&child, self.mut_indpb, mut_mu, mut_sigma);

                offspring.push(child);
            }
        }

        offspring
    }
}
