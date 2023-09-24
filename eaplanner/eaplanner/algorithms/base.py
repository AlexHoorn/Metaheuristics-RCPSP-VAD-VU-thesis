import csv
import json
import pickle
import shutil
from abc import abstractmethod
from datetime import datetime
from functools import partial
from pathlib import Path
from time import sleep

import numpy as np
import numpy.typing as npt
import pandas as pd
from deap import tools
from deap.base import Toolbox
from deap.tools import HallOfFame

from eaplanner.interpreter import ScheduleInterpreterBase
from eaplanner.utils import pareto_rank, rank_lexicographic

# Type hint that denotes a numpy array containing floats
Individual = npt.NDArray[np.float64]


class AlgorithmBase:
    def __init__(
        self,
        toolbox: Toolbox,
        interpreter: ScheduleInterpreterBase,
        max_evaluations: int,
        repair_pct: float = 1.0,
        halloffame: HallOfFame | None = None,
        verbose: bool = __debug__,
        save: bool = False,
        save_population: bool = False,
        folder: str | None = None,
    ):
        self.toolbox = toolbox
        self.interpreter = interpreter
        self.max_evaluations = max_evaluations
        self.interpreter.repair_pct = repair_pct
        self.halloffame = halloffame
        self.verbose = verbose
        self.save_population = save_population

        self.stats = self.statistics()

        if save:
            # Create a unique folder for the results
            while True:
                runtime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                if folder is not None:
                    self.folder = Path("results") / folder / f"{runtime}_{self!r}"
                else:
                    self.folder = Path("results") / f"{runtime}_{self!r}"

                try:
                    self.folder.mkdir(parents=True, exist_ok=False)
                    break
                except FileExistsError:
                    print("Folder already exists, trying again...")
                    sleep(1)
                    continue
        else:
            self.folder = None

        self._current_patience = 0

    def create_population(self, n: int) -> list[Individual]:
        return self.toolbox.population(n)  # type: ignore

    @staticmethod
    def statistics():
        stats = tools.Statistics(lambda ind: ind.fitness.values)  # type: ignore
        stats.register("avg", partial(np.mean, axis=0))
        stats.register("std", partial(np.std, axis=0))
        stats.register("min", partial(np.min, axis=0))
        stats.register("max", partial(np.max, axis=0))

        return stats

    def run(self):
        self._save_instance()

        self.logbook = tools.Logbook()
        self.logbook.header = ["gen", "nevals"] + self.stats.fields  # type: ignore

        population = self._create_population()
        invalid_ind = self._evaluate(population)

        evals = len(invalid_ind)
        self.current_evals = evals
        self._update_halloffame(population)
        self._update_logbook(population, 0, evals)
        self._save_population(0, population)

        population = self._run_evolution_loop(population)

        self._merge_populations()
        self._save_logbook()
        self._save_solution()

        return population, self.logbook

    def _evaluate(self, population: list[Individual]):
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]  # type: ignore
        results = self.toolbox.map(self.toolbox.evaluate, invalid_ind)  # type: ignore
        for ind, (fit, chromosone) in zip(invalid_ind, results):
            ind.fitness.values = fit  # type: ignore
            ind[:] = chromosone

        return invalid_ind

    def _sort_lexicographically(self, population: list[Individual]) -> list[Individual]:
        fitness = np.array([ind.fitness.values for ind in population])  # type: ignore
        order = np.lexsort(fitness[:, ::-1].T)

        return [population[i] for i in order]

    def _rank_fitness_lexicographic(self, population: list[Individual]):
        fitness = np.array([ind.fitness.values for ind in population])  # type: ignore
        ranks = rank_lexicographic(fitness)

        return ranks

    def _rank_fitness_pareto(self, population: list[Individual]):
        fitness = np.array([ind.fitness.values for ind in population])  # type: ignore
        ranks = pareto_rank(fitness)

        return ranks

    def _select(self, population: list[Individual], mu: int) -> list[Individual]:
        return self.toolbox.select(population, mu)  # type: ignore

    def _update_halloffame(self, population: list[Individual]):
        if self.halloffame is not None:
            self.halloffame.update(population)

    def _update_logbook(self, population: list[Individual], gen: int, n_evals: int):
        record = self._compile_stats(population)
        self.logbook.record(gen=gen, nevals=n_evals, **record)

        if self.verbose:
            print(self.logbook.stream)

    def _compile_stats(self, population: list[Individual]):
        return self.stats.compile(population)

    def _population_files_gen(self):
        if self.folder:
            population_files = (self.folder / "population").glob("*.csv")
            for file in population_files:
                df = pd.read_csv(file)
                df["gen"] = int(file.stem)
                yield df

    def _merge_populations(self, delete: bool = True):
        if self.folder and self.save_population:
            population = pd.concat(self._population_files_gen()).sort_values(by="gen")
            population.reset_index(drop=True).to_feather(
                self.folder / "population.feather"
            )

            if delete:
                shutil.rmtree(self.folder / "population")

    def _save_logbook(self):
        if self.folder:
            df = pd.DataFrame(self.logbook)
            score_names = self.interpreter.score_names

            for stat in ["avg", "min", "max", "std"]:
                for i, score_name in enumerate(score_names):
                    df[f"{stat}_{score_name}"] = df[stat].apply(lambda x: x[i])

            df.drop(columns=["avg", "min", "max", "std"], inplace=True)
            df.to_csv(self.folder / "logbook.csv", index=False)

    def _save_solution(self):
        if self.folder and self.halloffame:
            best: Individual = self.halloffame[0]
            scores = {
                s: v for s, v in zip(self.interpreter.score_names, best.fitness.values)  # type: ignore
            }
            solution = {"individual": best.tolist(), "scores": scores}

            with (self.folder / "solution.json").open("w") as f:
                json.dump(solution, f, indent=4)

    def _save_population(self, gen: int, population: list[Individual]):
        if self.folder and self.save_population:
            pop_dir = self.folder / "population"
            pop_dir.mkdir(parents=True, exist_ok=True)

            with open(pop_dir / f"{gen}.csv", mode="w+", newline="") as csv_file:
                fieldnames = [f"gene_{i}" for i in range(len(population[0]))]
                fieldnames.extend([f"score_{s}" for s in self.interpreter.score_names])
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for ind in population:
                    row = {f"gene_{i}": gene for i, gene in enumerate(ind)}
                    row.update({f"score_{s}": score for s, score in zip(self.interpreter.score_names, ind.fitness.values)})  # type: ignore
                    writer.writerow(row)

    def _save_instance(self):
        if self.folder and self.interpreter:
            with (self.folder / "instance.pkl").open("wb") as f:
                pickle.dump(self.interpreter, f)

    @abstractmethod
    def _run_evolution_loop(self, population: list[Individual]) -> list[Individual]:
        raise NotImplementedError

    @abstractmethod
    def _create_population(self) -> list[Individual]:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    def repr_toolbox(self) -> str:
        strings = [f"repair_pct={self.interpreter.repair_pct}"]
        if hasattr(self.toolbox, "mate"):
            mate = self.toolbox.mate.keywords  # type: ignore
            strings.append(", ".join([f"mate_{k}={v}" for k, v in mate.items()]))

        if hasattr(self.toolbox, "mutate"):
            mutate = self.toolbox.mutate.keywords  # type: ignore
            strings.append(", ".join([f"mutate_{k}={v}" for k, v in mutate.items()]))

        return ", ".join(strings)


def check_individual(func):
    def wrappper(*args, **kargs):
        children = func(*args, **kargs)
        for c in children:
            c[c < 0] = 0
        return children

    return wrappper
