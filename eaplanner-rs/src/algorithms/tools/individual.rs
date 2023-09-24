use rand::Rng;

use super::utils::is_smaller_or_equal_lexicographic;

#[derive(Clone, Debug, PartialEq)]
pub struct Individual {
    pub chromosome: Vec<f32>,
    pub fitness: Option<Vec<i32>>,
}

impl Individual {
    pub fn new(size: usize) -> Self {
        Self {
            chromosome: vec![0.0; size],
            fitness: None,
        }
    }

    pub fn from_vec(chromosome: Vec<f32>) -> Self {
        Self {
            chromosome,
            fitness: None,
        }
    }
}

#[derive(Clone, Debug)]
pub struct Particle {
    pub individual: Individual,
    pub velocity: Vec<f32>,
    pub best: Individual,
}

impl Particle {
    pub fn new(individual: Individual, smax: f32, smin: f32) -> Self {
        let mut rng = rand::thread_rng();
        let velocity = (0..individual.chromosome.len())
            .map(|_| rng.gen_range(smin..=smax))
            .collect::<Vec<f32>>();
        let best = individual.clone();
        Self {
            individual,
            velocity,
            best,
        }
    }

    pub fn update_particle(
        &mut self,
        weight: f32,
        phi1: f32,
        phi2: f32,
        smax: f32,
        smin: f32,
        global_best: &Individual,
    ) {
        let mut rng = rand::thread_rng();
        for (i, gene) in self.individual.chromosome.iter_mut().enumerate() {
            let u1 = rng.gen::<f32>();
            let u2 = rng.gen::<f32>();

            let v_u1 = phi1 * u1 * (self.best.chromosome[i] - *gene);
            let v_u2 = phi2 * u2 * (global_best.chromosome[i] - *gene);

            let v = weight * self.velocity[i] + v_u1 + v_u2;

            // Check if velocity is within bounds
            if v > smax {
                self.velocity[i] = smax;
            } else if v < smin {
                self.velocity[i] = smin;
            } else {
                self.velocity[i] = v;
            }

            *gene += self.velocity[i];
        }

        self.individual.fitness = None;
    }

    pub fn update_best(&mut self, new: &Individual) {
        if is_smaller_or_equal_lexicographic(
            new.fitness.as_ref().unwrap(),
            self.individual.fitness.as_ref().unwrap(),
        ) {
            self.best = new.clone();
        }
    }
}
