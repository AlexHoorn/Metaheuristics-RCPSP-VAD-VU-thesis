use crate::algorithms::tools::{
    individual::Individual,
    variation::{crossover, mutate},
};

#[test]
fn test_crossover() {
    let parent1_chromosome = vec![1.0; 10];
    let mut parent1 = Individual::from_vec(parent1_chromosome.clone());
    parent1.fitness = Some(vec![1; 2]);

    let parent2_chromosome = vec![2.0; 10];
    let mut parent2 = Individual::from_vec(parent2_chromosome.clone());
    parent2.fitness = Some(vec![2; 2]);

    let child = crossover(&parent1, &parent2);

    // Check that parents are not modified
    assert_eq!(parent1.chromosome, vec![1.0; 10]);
    assert_eq!(parent1.fitness, Some(vec![1; 2]));
    assert_eq!(parent2.chromosome, vec![2.0; 10]);
    assert_eq!(parent2.fitness, Some(vec![2; 2]));

    // Check that child is a crossover of parents
    assert!(child.chromosome.iter().all(|&x| x == 1.0 || x == 2.0));
    assert_eq!(child.fitness, None);
}

#[test]
fn test_mutate() {
    let indpb = 0.5;
    let mut_mu = 0.0;
    let mut_sigma = 1.0;

    let mut ind = Individual::from_vec(vec![1.0; 10]);
    ind.fitness = Some(vec![1; 2]);

    let mutated = mutate(&ind, indpb, mut_mu, mut_sigma);

    // Check that ind is not modified
    assert_eq!(ind.chromosome, vec![1.0; 10]);
    assert_eq!(ind.fitness, Some(vec![1; 2]));

    // Check that mutated is a mutation of ind
    assert_ne!(mutated.chromosome, vec![1.0; 10]);
    assert_eq!(mutated.fitness, None);
}
