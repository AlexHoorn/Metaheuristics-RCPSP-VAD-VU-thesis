import numpy as np

from eaplanner.algorithms.base import AlgorithmBase, Individual


class PlantPropagation(AlgorithmBase):
    def __init__(
        self,
        mu: int,
        lambda_: int,
        mut_std: float,
        mut_indpb: float,
        *args,
        **kwargs,
    ):
        self.mu = mu
        self.lambda_ = lambda_
        self.mut_std = mut_std
        self.mut_indpb = mut_indpb

        super().__init__(*args, **kwargs)

    def _create_population(self):
        return self.create_population(self.mu)

    def _run_evolution_loop(self, population: list[Individual]):
        gen = 1
        while self.current_evals < self.max_evaluations:
            offspring = self._create_offspring(population)
            invalid_ind = self._evaluate(offspring)

            population = self.toolbox.select(population + offspring, self.mu)  # type: ignore

            evals = len(invalid_ind)
            self.current_evals += evals
            self._update_logbook(population, gen, evals)
            self._save_population(gen, population)

            self._update_halloffame(offspring)
            gen += 1

        return population

    def _ppa_fitness(self, fitness_values: np.ndarray):
        fitness = np.array(fitness_values)
        fitness: np.ndarray = (len(fitness) - fitness) / (len(fitness) - 1)
        fitness = 0.5 * (np.tanh(4 * fitness - 2) + 1)

        return fitness

    def _determine_n_offspring(self, fitness: np.ndarray) -> list[int]:
        return (
            np.ceil(self.lambda_ * fitness * np.random.uniform(0, 1, len(fitness)))
            .astype(np.int_)
            .tolist()
        )

    def _create_offspring(self, population: list[Individual]):
        ranks = self._rank_fitness_pareto(population)
        fitness = self._ppa_fitness(ranks)
        n_offspring = self._determine_n_offspring(fitness)
        offspring = []

        for ind, n, ind_fit in zip(population, n_offspring, fitness):
            for _ in range(n):
                child = self.toolbox.clone(ind)  # type: ignore
                mutation = (
                    2
                    * np.random.uniform(-self.mut_std, self.mut_std, len(child))
                    * (1 - ind_fit)
                )
                mutation = np.where(
                    np.random.uniform(0, 1, len(child)) < self.mut_indpb, mutation, 0
                )
                child[:] = child + mutation
                del child.fitness.values
                offspring.append(child)

        return offspring

    def __repr__(self):
        return f"PlantPropagation(mu={self.mu}, lambda_={self.lambda_}, mut_std={self.mut_std}, mut_indpb={self.mut_indpb}, {self.repr_toolbox()})"
