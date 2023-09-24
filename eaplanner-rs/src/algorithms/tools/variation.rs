use rand::Rng;
use rand_distr::StandardNormal;

use super::individual::Individual;

pub fn crossover(parent1: &Individual, parent2: &Individual) -> Individual {
    let mut child = Individual::from_vec(parent1.chromosome.clone());

    for i in 0..child.chromosome.len() {
        if rand::random() {
            child.chromosome[i] = parent2.chromosome[i];
        }
    }

    child
}

pub fn mutate(ind: &Individual, indpb: f32, mut_mu: f32, mut_sigma: f32) -> Individual {
    let mut ind = Individual::from_vec(ind.chromosome.clone());
    let mut rng = rand::thread_rng();

    for i in 0..ind.chromosome.len() {
        if rng.gen::<f32>() <= indpb {
            ind.chromosome[i] += (rng.sample::<f32, _>(StandardNormal) + mut_mu) * mut_sigma;
        }
    }

    ind
}
