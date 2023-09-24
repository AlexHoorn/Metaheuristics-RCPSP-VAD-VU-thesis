use std::path::Path;

use crate::algorithms::tools::individual::Individual;

pub struct Logbook {
    generations: Vec<i32>,
    evaluations: Vec<i32>,
    mean: Vec<Vec<f32>>,
    std: Vec<Vec<f32>>,
    min: Vec<Vec<f32>>,
    max: Vec<Vec<f32>>,
}

impl Logbook {
    pub fn new() -> Self {
        Self {
            generations: Vec::new(),
            evaluations: Vec::new(),
            mean: Vec::new(),
            std: Vec::new(),
            min: Vec::new(),
            max: Vec::new(),
        }
    }

    pub fn record(
        &mut self,
        generation: i32,
        evaluations: i32,
        population: &Vec<Individual>,
        verbose: bool,
    ) {
        self.generations.push(generation);
        self.evaluations.push(evaluations);

        let num_individuals = population.len();
        let num_objectives = population[0].fitness.as_ref().unwrap().len();

        let mut mean = vec![0.0; num_objectives];
        let mut std = vec![0.0; num_objectives];
        let mut min = vec![0.0; num_objectives];
        let mut max = vec![0.0; num_objectives];

        for i in 0..num_individuals {
            let fitness = population[i].fitness.as_ref().unwrap();
            for j in 0..num_objectives {
                mean[j] += fitness[j] as f32;
                std[j] += fitness[j] as f32 * fitness[j] as f32;
                if i == 0 || fitness[j] < min[j] as i32 {
                    min[j] = fitness[j] as f32;
                }
                if i == 0 || fitness[j] > max[j] as i32 {
                    max[j] = fitness[j] as f32;
                }
            }
        }

        for j in 0..num_objectives {
            mean[j] /= num_individuals as f32;
            std[j] = (std[j] / num_individuals as f32 - mean[j] * mean[j]).sqrt();
        }

        self.mean.push(mean);
        self.std.push(std);
        self.min.push(min);
        self.max.push(max);

        if verbose {
            let i = self.generations.len() - 1;
            println!(
                "Generation {}, evaluations {}, mean {:?}, std {:?}, min {:?}, max {:?}",
                generation, evaluations, self.mean[i], self.std[i], self.min[i], self.max[i]
            );
        }
    }

    pub fn write_to_csv(&self, save_folder: &Path) {
        let filepath = save_folder.join("logbook.csv");
        let file = std::fs::File::create(filepath).expect("Failed to create file");
        let mut writer = csv::Writer::from_writer(file);

        // write header
        writer
            .write_record(&["generation", "evaluations", "mean", "std", "min", "max"])
            .expect("Failed to write header");

        // write data
        for i in 0..self.generations.len() {
            writer
                .write_record(&[
                    self.generations[i].to_string(),
                    self.evaluations[i].to_string(),
                    self.mean[i]
                        .iter()
                        .map(|f| f.to_string())
                        .collect::<Vec<String>>()
                        .join(";"),
                    self.std[i]
                        .iter()
                        .map(|f| f.to_string())
                        .collect::<Vec<String>>()
                        .join(";"),
                    self.min[i]
                        .iter()
                        .map(|f| f.to_string())
                        .collect::<Vec<String>>()
                        .join(";"),
                    self.max[i]
                        .iter()
                        .map(|f| f.to_string())
                        .collect::<Vec<String>>()
                        .join(";"),
                ])
                .expect("Failed to write data");
        }
    }
}
