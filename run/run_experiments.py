import json
from os import cpu_count
import random
import subprocess
from datetime import datetime
from glob import glob
from itertools import product
from pathlib import Path

from mpire import WorkerPool as Pool
from mpire.dashboard import start_dashboard

if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    dashboard_details = start_dashboard()
    print(dashboard_details)

    algorithm_params: dict[str, dict[str, float | int]] = {
        "ga": {
            "mu": 200,
            "lambda_": 200,
            "cxpb": 0.5,
            "cx_indpb": 0.5,
            "mut_indpb": 0.5,
            "mut_sigma": 2,
            "repair_pct": 1.0,
        },
        "ppa": {
            "mu": 200,
            "lambda_": 10,
            "mut_indp": 0.5,
            "mut_sigma": 2,
            "repair_pct": 1.0,
        },
        "pso": {
            "mu": 200,
            "phi1": 4,
            "phi2": 6,
            "smax": 2,
            "weight": 1,
            "repair_pct": 1.0,
        },
        "sa": {
            "mu": 1,
            "mut_indpb": 0.1,
            "mut_sigma": 1.0,
            "temp": 100,
            "alpha": 0.99,
            "repair_pct": 1.0,
        },
        "shc": {
            "mu": 1,
            "mut_indpb": 0.4,
            "mut_sigma": 1.0,
            "repair_pct": 1.0,
        },
    }
    algorithm_names = {
        "ga": "MuPlusLambda",
        "ppa": "PlantPropagation",
        "pso": "ParticleSwarm",
        "sa": "SimulatedAnnealing",
        "shc": "StochasticHillClimb",
    }
    global_flags = [
        "disable_multiprocessing",
        "seed",
        "quiet",
    ]
    global_str = " ".join([f"--{v}" for v in global_flags])

    # number of times each task should be run
    repeats = 3

    # find all instances
    instances = [
        Path(p)
        for p in glob(
            str(curr_dir.parent / "instances" / "generated") + "/**/*.pkl",
            recursive=True,
        )
    ]

    # find all tasks that have already been run
    done_tasks = glob(
        f"{str(curr_dir.parent)}/results/**/solution.json", recursive=True
    )

    tasks = []
    for (algorithm, params), instance in product(algorithm_params.items(), instances):
        # check how often task has already been run
        n_runs = sum(
            algorithm_names[algorithm] in task and instance.name[:-4] in task
            for task in done_tasks
        )

        if n_runs >= repeats:
            continue

        # add tasks to list
        params_str = " ".join([f"--{k} {v}" for k, v in params.items()])
        alg_file = curr_dir / f"algorithm_{algorithm}.py"
        task = f"python -O {alg_file} {params_str} {global_str} --instance {instance}"
        tasks.extend([task] * (repeats - n_runs))

    random.shuffle(tasks)

    print(f"Running {len(tasks)} tasks")
    if not tasks:
        print("No tasks to run")
        exit()

    # run tasks
    with Pool(cpu_count() or 2 - 1, enable_insights=True) as p:
        for res in p.imap_unordered(subprocess.run, tasks, progress_bar=True):
            continue

        insights = p.get_insights()

    # save mpire insights
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json.dump(insights, open(curr_dir / f"insights_{date_str}.json", "w"))
