use std::path::{Path, PathBuf};

use rand::Rng;

use crate::algorithms::tools::hall_of_fame::HallOfFame;
use crate::algorithms::tools::individual::Individual;
use crate::algorithms::tools::logbook::Logbook;
use crate::interpreter::Interpreter;

pub trait Algorithm {
    fn base(&mut self) -> &mut AlgorithmBase;
    fn run(&mut self);
}

pub struct AlgorithmBase {
    pub mu: i32,
    repair_pct: f32,
    pub max_evaluations: i32,
    pmin: i32,
    pmax: i32,
    pub interpreter: Box<dyn Interpreter>,
    pub hall_of_fame: HallOfFame,
    verbose: bool,
    save_population: bool,
    save_folder: PathBuf,
    pub logbook: Logbook,
    pub original_penalty: i32,
    pub original_makespan: i32,
}

impl AlgorithmBase {
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
        algorithm_name: String,
    ) -> Self {
        let save_folder = {
            loop {
                let runtime = chrono::Local::now().format("%Y-%m-%d_%H-%M-%S").to_string();
                let curr_folder = Path::new("results")
                    .join(&save_folder)
                    .join(format!("{}_{}", runtime, algorithm_name));
                if !curr_folder.exists() {
                    std::fs::create_dir_all(&curr_folder).expect("Failed to create folder");
                    break curr_folder;
                }
            }
        };

        let original_scores = interpreter.get_scores();

        Self {
            mu,
            repair_pct,
            max_evaluations,
            pmin,
            pmax,
            interpreter,
            hall_of_fame: HallOfFame::new(1),
            verbose,
            save_population,
            save_folder,
            logbook: Logbook::new(),
            original_penalty: original_scores[0],
            original_makespan: original_scores[1],
        }
    }

    fn save_instance(&self) {
        let filepath = self.save_folder.join("instance");
        if !filepath.exists() {
            std::fs::create_dir_all(&filepath).expect("Failed to create folder");
        }

        self.interpreter.get_schedule().to_csv(&filepath);
    }

    fn create_population(&self, n: i32, init: Vec<f32>, pmin: i32, pmax: i32) -> Vec<Individual> {
        let mut rng = rand::thread_rng();
        let mut population = Vec::new();
        for _ in 0..n {
            let mut chromosome = init.clone();
            for gene in chromosome.iter_mut() {
                *gene = rng.gen_range(pmin..=pmax) as f32;
            }
            let individual = Individual::from_vec(chromosome);
            population.push(individual);
        }
        population
    }

    pub fn evaluate(&mut self, population: &mut Vec<Individual>) -> i32 {
        let mut evaluations = 0;

        for individual in population.iter_mut() {
            evaluations += self.evaluate_single(individual) as i32;
        }

        evaluations
    }

    pub fn evaluate_single(&mut self, individual: &mut Individual) -> bool {
        if individual.fitness.is_some() {
            return false;
        }

        let fitness = self.interpreter.evaluate(individual, self.repair_pct);
        individual.fitness = Some(fitness);
        let chromosome = self.interpreter.get_chromosome();
        individual.chromosome = chromosome;

        true
    }

    pub fn run_start(&mut self) -> (Vec<Individual>, i32) {
        self.save_instance();

        let mut population = self.create_population(
            self.mu,
            self.interpreter.get_chromosome().clone(),
            self.pmin,
            self.pmax,
        );
        let evaluations = self.evaluate(&mut population);
        self.hall_of_fame.update(&population);

        (population, evaluations)
    }

    pub fn run_finish(&self) {
        // self.merge_populations();
        self.save_logbook();
        self.save_solution();
    }

    pub fn save_population(&self, population: &Vec<Individual>, generation: i32) {
        if !self.save_population {
            return;
        }

        // create csv file
        let filepath = self
            .save_folder
            .join(format!("population_{}.csv", generation));
        let file = std::fs::File::create(filepath).expect("Failed to create file");
        let mut writer = csv::Writer::from_writer(file);

        // write header
        writer
            .write_record(&["gen", "fitness", "chromosome"])
            .expect("Failed to write header");

        // write data
        for individual in population.iter() {
            writer
                .write_record(&[
                    generation.to_string(),
                    individual
                        .fitness
                        .as_ref()
                        .unwrap()
                        .iter()
                        .map(|f| f.to_string())
                        .collect::<Vec<String>>()
                        .join(";"),
                    individual
                        .chromosome
                        .iter()
                        .map(|f| f.to_string())
                        .collect::<Vec<String>>()
                        .join(";"),
                ])
                .expect("Failed to write data");
        }
    }

    pub fn update_logbook(
        &mut self,
        generation: i32,
        evaluations: i32,
        population: &Vec<Individual>,
    ) {
        self.logbook
            .record(generation, evaluations, population, self.verbose);

        if self.verbose {
            let best = self.hall_of_fame.get(0);
            println!(
                "Generation: {}, Evaluations: {}, Best: {:?}",
                generation, evaluations, best.fitness,
            );
        }
    }

    pub fn save_logbook(&self) {
        self.logbook.write_to_csv(&self.save_folder);
    }

    pub fn save_solution(&self) {
        // write the original scores, best scores, and best chromosome to json
        let mut json_output = serde_json::Map::new();
        let mut original_scores = serde_json::Map::new();
        let mut solution_scores = serde_json::Map::new();

        // original scores
        original_scores.insert(
            "penalty".to_string(),
            serde_json::Value::Number(serde_json::Number::from(self.original_penalty)),
        );
        original_scores.insert(
            "makespan".to_string(),
            serde_json::Value::Number(serde_json::Number::from(self.original_makespan)),
        );

        // best scores
        let best = self.hall_of_fame.get(0);
        solution_scores.insert(
            "penalty".to_string(),
            serde_json::Value::Number(serde_json::Number::from(best.fitness.as_ref().unwrap()[0])),
        );
        solution_scores.insert(
            "makespan".to_string(),
            serde_json::Value::Number(serde_json::Number::from(best.fitness.as_ref().unwrap()[1])),
        );

        // add scores to json
        json_output.insert(
            "original_scores".to_string(),
            serde_json::Value::Object(original_scores),
        );
        json_output.insert(
            "scores".to_string(),
            serde_json::Value::Object(solution_scores),
        );

        let solution_chromosome = serde_json::Value::Array(
            best.chromosome
                .iter()
                .map(|f| serde_json::Value::Number(serde_json::Number::from(*f as i32)))
                .collect(),
        );
        json_output.insert("individual".to_string(), solution_chromosome);

        let filepath = self.save_folder.join("solution.json");
        let file = std::fs::File::create(filepath).expect("Failed to create file");
        serde_json::to_writer_pretty(file, &json_output).expect("Failed to write solution");
    }
}
