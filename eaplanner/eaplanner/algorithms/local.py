import random

import numpy as np

from eaplanner.algorithms.base import AlgorithmBase, Individual
from eaplanner.utils import is_smaller_or_equal_lexicographic


class StochasticHillClimb(AlgorithmBase):
    def __init__(
        self,
        mu: int,
        mut_prob: float,
        mut_std: float,
        *args,
        **kwargs,
    ):
        self.mu = mu
        self.mut_prob = mut_prob
        self.mut_std = mut_std

        super().__init__(*args, **kwargs)

    def _create_population(self):
        return self.create_population(self.mu)

    def _run_evolution_loop(self, population: list[Individual]):
        gen = 1
        while self.current_evals < self.max_evaluations:
            offspring = self._create_offspring(population)
            invalid_ind = self._evaluate(offspring)

            for i, (ind, off) in enumerate(zip(population, offspring)):
                if is_smaller_or_equal_lexicographic(off.fitness.values, ind.fitness.values):  # type: ignore
                    population[i] = off

            evals = len(invalid_ind)
            self.current_evals += evals
            self._update_logbook(population, gen, evals)
            self._save_population(gen, population)

            self._update_halloffame(offspring)
            gen += 1

        return population

    def _create_offspring(self, population: list[Individual]):
        offspring = self.toolbox.clone(population)  # type: ignore
        for ind in offspring:
            mask = np.random.uniform(0, 1, size=len(ind)) < self.mut_prob
            mutation = np.random.uniform(-self.mut_std, self.mut_std, size=len(ind))
            ind[:] = np.where(mask, ind[:] + mutation, ind[:])
            del ind.fitness.values

        return offspring

    def __repr__(self):
        return f"{self.__class__.__name__}(mu={self.mu}, mut_prob={self.mut_prob}, mut_std={self.mut_std}, {self.repr_toolbox()})"


class SimulatedAnnealing(StochasticHillClimb):
    def __init__(
        self,
        temp: float,
        alpha: float,
        *args,
        **kwargs,
    ):
        self.temp = temp
        self.alpha = alpha

        super().__init__(*args, **kwargs)

    def _run_evolution_loop(self, population: list[Individual]):
        temp = self.temp
        gen = 1

        while self.current_evals < self.max_evaluations:
            offspring = self._create_offspring(population)
            invalid_ind = self._evaluate(offspring)

            for i, (ind, off) in enumerate(zip(population, offspring)):
                if is_smaller_or_equal_lexicographic(off.fitness.values, ind.fitness.values):  # type: ignore
                    population[i] = off

                elif random.uniform(0, 1) < self._transition_probability(
                    ind.fitness.values, off.fitness.values, temp  # type: ignore
                ):
                    population[i] = off

            evals = len(invalid_ind)
            self.current_evals += evals

            self._update_logbook(population, gen, evals)
            self._save_population(gen, population)

            self._update_halloffame(offspring)

            temp *= self.alpha
            gen += 1

        return population

    def _transition_probability(self, fitness_old, fitness_new, temp):
        delta_f = np.array(fitness_old) - np.array(fitness_new)

        return np.exp((-delta_f).sum() / temp)

    def __repr__(self):
        return f"{self.__class__.__name__}(mu={self.mu}, mut_prob={self.mut_prob}, mut_std={self.mut_std}, temp={self.temp}, alpha={self.alpha}, {self.repr_toolbox()})"
