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
    MU,
    NEVAL,
    PATIENCE,
    PHI1,
    PHI2,
    PMAX,
    PMIN,
    QUIET,
    REPAIR_PCT,
    SAVE_POPULATION,
    SEED,
    SMAX,
    WEIGHT,
    WEIGHTS,
)

from eaplanner.algorithms.pso import ParticleSwarm
from eaplanner.entities.schedule import Schedule
from eaplanner.interpreter import AbsoluteScheduleInterpreter
from eaplanner.utils import LexHallOfFame
from eaplanner.visualization import ResultVisualization

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
    "--smax", type=float, default=SMAX, help="Maximum speed value for a gene"
)
parser.add_argument(
    "--phi1", type=float, default=PHI1, help="Minimum pulling force for a gene"
)
parser.add_argument(
    "--phi2", type=float, default=PHI2, help="Maximum pulling force for a gene"
)
parser.add_argument("--weight", type=float, default=WEIGHT, help="Weight for inertia")
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


def generate(
    pmin: float,
    pmax: float,
    smin: float,
    smax: float,
    seed: np.ndarray | None = None,
    size: int | None = None,
):
    if seed is None:
        seed = np.random.uniform(pmin, pmax, size)

    size = len(seed)
    part = creator.Particle(seed + np.random.randint(pmin, pmax, size))  # type: ignore
    part.speed = np.random.uniform(smin, smax, size)
    return part


# create and run evolutionary algorithm
creator.create("FitnessMin", base.Fitness, weights=args.weights)
creator.create("Particle", np.ndarray, fitness=creator.FitnessMin, speed=list, best=None)  # type: ignore

# initialization of individuals and population
toolbox = base.Toolbox()
toolbox.register(
    "particle",
    generate,
    seed=interpreter.to_chromosome() if args.seed else None,
    pmin=args.pmin,
    pmax=args.pmax,
    smin=-args.smax,
    smax=args.smax,
    size=2 * len(interpreter.schedule),
)
toolbox.register("population", tools.initRepeat, list, toolbox.particle)  # type: ignore

# evolutionary operators
toolbox.register("evaluate", interpreter.interpret_and_get_scores)

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
    ea = ParticleSwarm(
        max_evaluations=args.neval,
        mu=args.mu,
        phi1=args.phi1,
        phi2=args.phi2,
        smin=-args.smax,
        smax=args.smax,
        weight=args.weight,
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
