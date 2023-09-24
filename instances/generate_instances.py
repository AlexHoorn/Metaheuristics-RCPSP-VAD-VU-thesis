from functools import partial
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from typing import Literal
import numpy as np

import seaborn as sns

from eaplanner.generation import ScheduleGenerator
from tqdm import tqdm

sns.set()


def generate_and_save(
    fname: str,
    n_assignments: int,
    n_resources: int | Literal["auto"] = "auto",
    p_date: float = 0.16,
    k: int = 1,
):
    schedule = ScheduleGenerator.generate_random_schedule(
        n_assignments=n_assignments, p_date=p_date, k=k, n_resources=n_resources
    )

    save_dir = Path(__file__).parent / "generated_param_search" / f"n_{n_assignments}"
    save_dir.mkdir(parents=True, exist_ok=True)
    schedule.save(save_dir / f"{fname}.pkl")
    schedule.save_csv(save_dir / fname)


if __name__ == "__main__":
    tasks = []

    # Used to generate the parameter search instances
    # N_ASSIGNMENTS = [100]
    # N_RESOURCES = ["auto"]
    # P_DATE = [0]
    # K = [1]
    # REPEAT = range(5)

    # for i, n_asg, n_res, p_date, k in product(
    #     REPEAT, N_ASSIGNMENTS, N_RESOURCES, P_DATE, K
    # ):
    #     tasks.append(
    #         (f"schedule_{n_asg}_{n_res}_{p_date}_{k}_{i}", n_asg, n_res, p_date, k)
    #     )

    N_ASSIGNMENTS = partial(np.random.randint, 10, 500)
    N_RESOURCES = partial(np.random.randint, 1, 20)
    P_DATE = lambda: 0.0
    K = partial(np.random.randint, 1, 5)
    REPEAT = range(1000)

    for i in REPEAT:
        tasks.append((f"schedule_{i}", N_ASSIGNMENTS(), N_RESOURCES(), P_DATE(), K()))

    with Pool() as p:
        p.starmap(generate_and_save, tqdm(tasks))
