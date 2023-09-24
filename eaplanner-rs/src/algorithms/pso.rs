use crate::interpreter::Interpreter;

use super::{
    base::{Algorithm, AlgorithmBase},
    tools::individual::{Individual, Particle},
};

pub struct ParticleSwarmOptimization {
    base: AlgorithmBase,
    phi1: f32,
    phi2: f32,
    smax: f32,
    smin: f32,
    weight: f32,
}

impl ParticleSwarmOptimization {
    pub fn new(
        mu: i32,
        phi1: f32,
        phi2: f32,
        smax: f32,
        smin: f32,
        weight: f32,
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
                "ParticleSwarm".to_string(),
            ),
            phi1,
            phi2,
            smax,
            smin,
            weight,
        }
    }

    fn update_particles(&self, particles: &mut Vec<Particle>, global_best: &Individual) {
        for particle in particles.iter_mut() {
            particle.update_particle(
                self.weight,
                self.phi1,
                self.phi2,
                self.smax,
                self.smin,
                global_best,
            )
        }
    }

    fn evaluate_particles(&mut self, particles: &mut Vec<Particle>) -> i32 {
        let mut evaluations = 0;
        for particle in particles.iter_mut() {
            evaluations += self.base.evaluate_single(&mut particle.individual) as i32;
        }

        evaluations
    }
}

impl Algorithm for ParticleSwarmOptimization {
    fn run(&mut self) {
        let mut generation = 1;
        let (start_population, mut evaluations) = self.base.run_start();
        let mut particles = start_population
            .iter()
            .map(|ind| Particle::new(ind.clone(), self.smax, self.smin))
            .collect::<Vec<Particle>>();

        while evaluations < self.base.max_evaluations {
            let global_best = self.base.hall_of_fame.get(0).clone();

            self.update_particles(&mut particles, &global_best);
            evaluations += self.evaluate_particles(&mut particles);

            let population = particles
                .iter()
                .map(|p| p.individual.clone())
                .collect::<Vec<Individual>>();
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
