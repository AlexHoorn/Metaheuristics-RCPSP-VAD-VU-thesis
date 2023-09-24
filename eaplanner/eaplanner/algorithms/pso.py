import math

import numpy as np
from deap import creator

from eaplanner.algorithms.base import AlgorithmBase, Individual
from eaplanner.utils import is_smaller_or_equal_lexicographic


class ParticleSwarm(AlgorithmBase):
    def __init__(
        self,
        mu: int,
        phi1: float,
        phi2: float,
        smin: float,
        smax: float,
        weight: float,
        *args,
        **kwargs,
    ):
        self.mu = mu
        self.phi1 = phi1
        self.phi2 = phi2
        self.smin = smin
        self.smax = smax
        self.weight = weight

        super().__init__(*args, **kwargs)

    def _create_population(self):
        return self.create_population(self.mu)

    def _run_evolution_loop(self, population: list[Individual]):
        best = None
        gen = 1

        while self.current_evals < self.max_evaluations:
            for part in population:
                if part.best is None or is_smaller_or_equal_lexicographic(  # type: ignore
                    part.fitness.values, part.best.fitness.values  # type: ignore
                ):
                    part.best = creator.Particle(part)  # type: ignore
                    part.best.fitness.values = part.fitness.values  # type: ignore

            best = self._sort_lexicographically(
                population + [best] if best is not None else population
            )[0]

            for part in population:
                self.update_particle(part, best)  # type: ignore

            invalid_ind = self._evaluate(population)

            evals = len(invalid_ind)
            self.current_evals += evals
            self._update_logbook(population, gen, evals)
            self._save_population(gen, population)

            self._update_halloffame(population)
            gen += 1

        return population

    def update_particle(self, part, best):
        u1 = np.random.uniform(0, self.phi1, len(part))
        u2 = np.random.uniform(0, self.phi2, len(part))
        v_u1 = u1 * (part.best - part)
        v_u2 = u2 * (best - part)
        part.speed = self.weight * part.speed + v_u1 + v_u2
        np.clip(part.speed, self.smin, self.smax, out=part.speed)
        part += part.speed
        del part.fitness.values

    @staticmethod
    def _fitness_product(fitness: tuple[float, ...]) -> float:
        return math.prod(max(1, f) for f in fitness)

    def __repr__(self):
        return f"{self.__class__.__name__}(mu={self.mu}, phi1={self.phi1}, phi2={self.phi2}, smin={self.smin}, smax={self.smax}, weight={self.weight}, {self.repr_toolbox()})"
