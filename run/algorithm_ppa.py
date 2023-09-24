import argparse
from datetime import datetime
import sys
from functools import partial
from multiprocessing.pool import ThreadPool
from pathlib import Path

import numpy as np
from deap import base, creator, tools
from params import (
    CREATE_FIGURES,
    CREATE_VIDEO,
    DISABLE_MULTIPROCESSING,
    INSTANCE,
    LAMBDA_,
    MU,
    MUT_INDPB,
    MUT_SIGMA,
    NEVAL,
    PATIENCE,
    PMAX,
    PMIN,
    QUIET,
    REPAIR_PCT,
    SAVE_POPULATION,
    SEED,
    WEIGHTS,
)

from eaplanner.algorithms.ppa import PlantPropagation
from eaplanner.entities.schedule import Schedule
from eaplanner.interpreter import AbsoluteScheduleInterpreter
from eaplanner.utils import LexHallOfFame
from eaplanner.visualization import ResultVisualization


def generate(size: int, pmin: int, pmax: int, init: np.ndarray | None = None):
    random_array = np.random.randint(pmin, pmax, size=size)
    if init is None:
        return creator.Individual(random_array)  # type: ignore

    return creator.Individual(init + random_array)  # type: ignore


parser = argparse.ArgumentParser()
parser.add_argument("--instance", type=str, default=INSTANCE, help="Path to instance")
parser.add_argument("--pmin", type=int, default=PMIN, help="Minimum value for a gene")
parser.add_argument("--pmax", type=int, default=PMAX, help="Maximum value for a gene")
parser.add_argument("--weights", type=str, default=WEIGHTS, help="Weights for fitness")
parser.add_argument("--neval", type=int, default=NEVAL, help="Number of evaluations")
parser.add_argument(
    "--mu", type=int, default=MU, help="Number of individuals to select"
)
parser.add_argument(
    "--lambda_", type=int, default=LAMBDA_, help="Number of offspring"
)
parser.add_argument("--mut_indpb", type=float, default=MUT_INDPB, help="Mutation indpb")
parser.add_argument("--mut_sigma", type=float, default=MUT_SIGMA, help="Mutation sigma")
parser.add_argument(
    "--patience", type=int, default=PATIENCE, help="Patience for early stopping"
)
parser.add_argument("--repair_pct", type=float, default=REPAIR_PCT, help="Repair percentage")
parser.add_argument("--seed", action="store_true", help="Seed the initial population")
parser.add_argument("--create_figures", action="store_true", help="Create figures")
parser.add_argument("--create_video", action="store_true", help="Create video")
parser.add_argument(
    "--disable_multiprocessing",
    action="store_true",
    help="Disable multiprocessing",
)
parser.add_argument("--quiet", action="store_true", help="Disable verbose output")
parser.add_argument("--save_population", action="store_true", help="Save population")
parser.set_defaults(
    seed=SEED,
    create_figures=CREATE_FIGURES,
    create_video=CREATE_VIDEO,
    disable_multiprocessing=DISABLE_MULTIPROCESSING,
    quiet=QUIET,
    save_population=SAVE_POPULATION,
)
args = parser.parse_args()

instance_path = Path(args.instance)
interpreter = AbsoluteScheduleInterpreter(Schedule.load(instance_path))
instance_name = instance_path.stem

# create and run evolutionary algorithm
creator.create("FitnessMin", base.Fitness, weights=args.weights)
creator.create("Individual", np.ndarray, fitness=creator.FitnessMin)  # type: ignore

# initialization of individuals and population
toolbox = base.Toolbox()
toolbox.register(
    "individual",
    generate,
    size=2 * len(interpreter.schedule),
    pmin=args.pmin,
    pmax=args.pmax,
    init=interpreter.to_chromosome() if args.seed else None,
)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)  # type: ignore

# evolutionary operators
toolbox.register("evaluate", interpreter.interpret_and_get_scores)

# selection
ref_points = tools.uniform_reference_points(nobj=len(args.weights))
toolbox.register("select", tools.selNSGA3WithMemory(ref_points=ref_points))

if __name__ == "__main__":
    # parallelization if not in debug mode
    if sys.gettrace() is None and not args.disable_multiprocessing:
        toolbox.register("map", ThreadPool().imap_unordered)
        print("Running in parallel mode")

    # statistics
    stats = tools.Statistics(lambda ind: ind.fitness.wvalues)  # type: ignore
    stats.register("avg", partial(np.mean, axis=0))
    stats.register("std", partial(np.std, axis=0))
    stats.register("min", partial(np.min, axis=0))
    stats.register("max", partial(np.max, axis=0))

    # track best individuals
    hof = LexHallOfFame(1, similar=np.array_equal)  # type: ignore

    # run algorithm
    ea = PlantPropagation(
        max_evaluations=args.neval,
        mu=args.mu,
        lambda_=args.lambda_,
        mut_std=args.mut_sigma,
        mut_indpb=args.mut_indpb,
        toolbox=toolbox,
        interpreter=interpreter,
        halloffame=hof,
        verbose=not args.quiet,
        save=True,
        folder=instance_name,
        save_population=args.save_population,
        repair_pct=args.repair_pct,
    )
    start_time = datetime.now()
    final_pop, logbook = ea.run()
    end_time = datetime.now()
    if not args.quiet:
        print(f"Running time time: {(end_time - start_time).total_seconds()}s")

    if ea.folder and (args.create_figures or args.create_video):
        visualizer = ResultVisualization(ea.folder)
        if args.create_figures:
            visualizer.visualize_convergence(x_axis="nevals")
            visualizer.visualize_convergence(x_axis="gen")
            visualizer.visualize_solution(show_gantt_constraints=True)
            visualizer.visualize_generations_pca()
            visualizer.visualize_fitnesses()
        if args.create_video:
            visualizer.visualize_generations_video(show_gantt_constraints=True)
            visualizer.visualize_generations_pca_video()
