import json
import random
import subprocess
from datetime import datetime
from functools import partial
from glob import glob
from os import cpu_count
from pathlib import Path
from typing import Callable

from mpire import WorkerPool as Pool
from mpire.dashboard import start_dashboard

if __name__ == "__main__":
    dashboard_details = start_dashboard()
    print(dashboard_details)

    tasks_per_algorithm = 1000
    repeats = 1

    curr_dir = Path(__file__).parent
    instances = [
        Path(p)
        for p in glob(
            str(curr_dir.parent / "instances" / "generated_param_search" / "n_100") + "/**/*.pkl",
            recursive=True,
        )
    ]
    algorithm_params: dict[str, dict[str, Callable[..., float]]] = {
        "ga": {
            "mu": partial(random.randint, 10, 300),
            "lambda_": partial(random.randint, 10, 300),
            "cxpb": partial(random.uniform, 0, 1),
            "cx_indpb": partial(random.uniform, 0.01, 1),
            "mut_indpb": partial(random.uniform, 0.01, 1),
            "mut_sigma": partial(random.uniform, 0.1, 2),
            "repair_pct": partial(random.uniform, 0, 1),
        },
        "ppa": {
            "mu": partial(random.randint, 10, 300),
            "lambda_": partial(random.randint, 10, 300),
            "mut_indp": partial(random.uniform, 0.01, 1),
            "mut_sigma": partial(random.uniform, 0.1, 2),
            "repair_pct": partial(random.uniform, 0, 1),
        },
        "pso": {
            "mu": partial(random.randint, 10, 300),
            "smax": partial(random.uniform, 0.1, 2),
            "phi1": partial(random.uniform, 0.1, 10),
            "phi2": partial(random.uniform, 0.1, 10),
            "repair_pct": partial(random.uniform, 0, 1),
            "weight": partial(random.uniform, 0.1, 1),
        },
        "sa": {
            "mu": partial(random.randint, 1, 50),
            "temp": partial(random.uniform, 1, 200),
            "alpha": partial(random.uniform, 0.8, 0.99),
            "mut_indpb": partial(random.uniform, 0.01, 1),
            "mut_sigma": partial(random.uniform, 0.1, 2),
            "repair_pct": partial(random.uniform, 0, 1),
        },
        "shc": {
            "mu": partial(random.randint, 1, 50),
            "mut_indpb": partial(random.uniform, 0.01, 1),
            "mut_sigma": partial(random.uniform, 0.1, 2),
            "repair_pct": partial(random.uniform, 0, 1),
        },
    }
    global_flags = [
        "disable_multiprocessing",
        "seed",
        "quiet",
        "neval 100000"
    ]
    global_str = " ".join([f"--{v}" for v in global_flags])

    tasks = []
    for algorithm, params in algorithm_params.items():
        for _ in range(tasks_per_algorithm):
            params_str = " ".join([f"--{k} {round(v(), 2)}" for k, v in params.items()])
            alg_file = curr_dir / f"algorithm_{algorithm}.py"
            instance = random.choice(instances)
            tasks.append(f"python {alg_file} {params_str} --instance {instance} {global_str}")

    tasks = tasks * repeats
    random.shuffle(tasks)

    with Pool(cpu_count() or 2 - 1, enable_insights=True) as p:
        for res in p.imap_unordered(subprocess.run, tasks, progress_bar=True):
            continue

        insights = p.get_insights()

    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json.dump(insights, open(curr_dir / f"insights_{date_str}.json", "w"))
