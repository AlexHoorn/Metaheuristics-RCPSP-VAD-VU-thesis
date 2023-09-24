pub mod algorithms;
pub mod entities;
pub mod interpreter;
pub mod load_csv;
pub mod test;

use algorithms::{fix::FixerOnly, sa::SimulatedAnnealing};
use clap::Parser;
use interpreter::Interpreter;
use std::path::Path;

use crate::{
    algorithms::{base::Algorithm, pso::ParticleSwarmOptimization, shc::StochasticHillClimber},
    entities::schedule::Schedule,
    interpreter::AbsoluteScheduleInterpreter,
};

#[derive(Parser, Debug)]
#[clap(name = "eaplanner-rs", version = "0.1.0", author = "Alex Hoorn")]
struct Args {
    // setup
    #[clap(long, default_value = "shc")]
    algorithm: String,
    #[clap(
        long,
        default_value = "C:/Dev/eaplanner/instances/generated/n_150/schedule_445/"
    )]
    instance_path: String,

    // generic hyperparameters
    #[clap(long, default_value_t = 200)]
    mu: i32,
    #[clap(long, default_value_t = 200)]
    lamdba: i32,
    #[clap(long, default_value_t = 100000)]
    nevals: i32,
    #[clap(long, default_value_t = -50)]
    pmin: i32,
    #[clap(long, default_value_t = 50)]
    pmax: i32,
    #[clap(long, default_value_t = 0.5)]
    cxpb: f32,
    #[clap(long, default_value_t = 0.5)]
    mut_indpb: f32,
    #[clap(long, default_value_t = 0.0)]
    mut_mu: f32,
    #[clap(long, default_value_t = 2.0)]
    mut_sigma: f32,
    #[clap(long, default_value_t = 1.0)]
    repair_pct: f32,
    #[clap(long, default_value_t = false)]
    verbose: bool,
    #[clap(long, default_value_t = false)]
    save_population: bool,
    #[clap(long, default_value = "./")]
    save_path: String,

    // pso hyperparameters
    #[clap(long, default_value_t = -2.0)]
    smin: f32,
    #[clap(long, default_value_t = 2.0)]
    smax: f32,
    #[clap(long, default_value_t = 4.0)]
    phi1: f32,
    #[clap(long, default_value_t = 6.0)]
    phi2: f32,
    #[clap(long, default_value_t = 1.0)]
    weight: f32,

    // sa hyperparameters
    #[clap(long, default_value_t = 100.0)]
    temperature: f32,
    #[clap(long, default_value_t = 0.99)]
    cooling_rate: f32,
}

fn main() {
    let args = Args::parse();
    let path = Path::new(&args.instance_path);

    if !path.exists() {
        panic!("Path does not exist: {}", path.display());
    }

    let schedule_name = path.file_name().unwrap().to_str().unwrap().to_string();

    println!("Loading from: {}", path.display());
    let schedule = load_csv::load_schedule(path);

    let start_penalty = schedule.get_total_penalty();
    let start_makespan = schedule.get_total_makespan();

    println!("Starting penalty: {}", start_penalty);
    println!("Starting makespan: {}", start_makespan);

    let interpreter = Box::new(AbsoluteScheduleInterpreter::new(schedule));

    let mut optimizer: Box<dyn Algorithm>;
    match args.algorithm.as_str() {
        "shc" => {
            optimizer = Box::new(get_shc(args, interpreter, schedule_name));
        }
        "pso" => {
            optimizer = Box::new(get_pso(args, interpreter, schedule_name));
        }
        "sa" => {
            optimizer = Box::new(get_sa(args, interpreter, schedule_name));
        }
        "ga" => {
            let mut optimizer = get_ga(args, interpreter, schedule_name);
        }
        "ppa" => {
            let mut optimizer = get_ppa(args, interpreter, schedule_name);
        }
        "fixer" => {
            optimizer = Box::new(get_fixer(args, interpreter, schedule_name));
        }
        _ => panic!("Algorithm not found: {}", args.algorithm),
    }

    let now = std::time::Instant::now();
    optimizer.run();
    let elapsed = now.elapsed();
    println!("Elapsed: {:?}", elapsed);

    let base = optimizer.base();
    let solution = base.hall_of_fame.get(0);

    base.interpreter.interpret(&solution.chromosome);

    println!(
        "Solution penalty: {}",
        optimizer.base().interpreter.get_scores()[0]
    );
    println!(
        "Solution makespan: {}",
        optimizer.base().interpreter.get_scores()[1]
    );
}

fn get_shc(
    args: Args,
    interpreter: Box<dyn Interpreter>,
    save_folder: String,
) -> StochasticHillClimber {
    StochasticHillClimber::new(
        args.mu,
        args.mut_indpb,
        args.mut_mu,
        args.mut_sigma,
        args.repair_pct,
        args.nevals,
        args.pmin,
        args.pmax,
        interpreter,
        args.verbose,
        args.save_population,
        save_folder,
    )
}

fn get_sa(
    args: Args,
    interpreter: Box<dyn Interpreter>,
    save_folder: String,
) -> SimulatedAnnealing {
    SimulatedAnnealing::new(
        args.mu,
        args.mut_indpb,
        args.mut_mu,
        args.mut_sigma,
        args.temperature,
        args.cooling_rate,
        args.repair_pct,
        args.nevals,
        args.pmin,
        args.pmax,
        interpreter,
        args.verbose,
        args.save_population,
        save_folder,
    )
}

fn get_pso(
    args: Args,
    interpreter: Box<dyn Interpreter>,
    save_folder: String,
) -> ParticleSwarmOptimization {
    ParticleSwarmOptimization::new(
        args.mu,
        args.phi1,
        args.phi2,
        args.smax,
        args.smin,
        args.weight,
        args.repair_pct,
        args.nevals,
        args.pmin,
        args.pmax,
        interpreter,
        args.verbose,
        args.save_population,
        save_folder,
    )
}

fn get_fixer(args: Args, interpreter: Box<dyn Interpreter>, save_folder: String) -> FixerOnly {
    FixerOnly::new(
        args.mu,
        args.repair_pct,
        args.nevals,
        args.pmin,
        args.pmax,
        interpreter,
        args.verbose,
        args.save_population,
        save_folder,
    )
}
