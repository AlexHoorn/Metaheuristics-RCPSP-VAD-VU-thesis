from deap.algorithms import varOr

from eaplanner.algorithms.base import AlgorithmBase, Individual


class MuPlusLambda(AlgorithmBase):
    def __init__(
        self,
        mu: int,
        lambda_: int,
        cxpb: float,
        mutpb: float,
        *args,
        **kwargs,
    ):
        self.mu = mu
        self.lambda_ = lambda_
        self.cxpb = cxpb
        self.mutpb = mutpb

        super().__init__(*args, **kwargs)

    def _create_population(self):
        return self.create_population(self.mu)

    def _run_evolution_loop(self, population: list[Individual]):
        gen = 1

        while self.current_evals < self.max_evaluations:
            offspring = varOr(
                population, self.toolbox, self.lambda_, self.cxpb, self.mutpb
            )

            invalid_ind = self._evaluate(offspring)
            population[:] = self._select(population + offspring, self.mu)

            evals = len(invalid_ind)
            self.current_evals += evals
            self._update_logbook(population, gen, evals)
            self._save_population(gen, population)

            self._update_halloffame(offspring)
            gen += 1

        return population

    def __repr__(self):
        return f"{self.__class__.__name__}(mu={self.mu}, lambda_={self.lambda_}, cxpb={self.cxpb}, mutpb={self.mutpb}, {self.repr_toolbox()})"
