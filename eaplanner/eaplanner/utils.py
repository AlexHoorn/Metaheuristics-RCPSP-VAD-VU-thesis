import numpy as np
from deap.tools import HallOfFame


class LexHallOfFame(HallOfFame):
    def update(self, population):
        for ind in population:
            if len(self) == 0 and self.maxsize != 0:
                # Working on an empty hall of fame is problematic for the
                # "for else"
                self.insert(population[0])
                continue
            if (
                is_smaller_or_equal_lexicographic(
                    ind.fitness.values, self[-1].fitness.values
                )
                or len(self) < self.maxsize
            ):
                for hofer in self:
                    # Loop through the hall of fame to check for any
                    # similar individual
                    if self.similar(ind, hofer):
                        break
                else:
                    # The individual is unique and strictly better than
                    # the worst
                    if len(self) >= self.maxsize:
                        self.remove(-1)
                    self.insert(ind)


def is_smaller_or_equal_lexicographic(a: tuple[float, ...], b: tuple[float, ...]):
    """Compares two arrays lexicographically.

    Returns True if a < b, False otherwise."""
    a_arr = np.array(a)
    b_arr = np.array(b)

    # return true if both arrays are equal
    if (a_arr == b_arr).all():
        return True

    # finds index of the first non matching element
    idx = np.where((a_arr > b_arr) != (a_arr < b_arr))

    if len(idx[0]) == 0:
        return False

    idx = idx[0][0]

    return a_arr[idx] < b_arr[idx]


def rank_lexicographic(values: np.ndarray) -> np.ndarray:
    order = np.lexsort(values[:, ::-1].T)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(len(values))

    return ranks


def pareto_rank(arr):
    num_rows, num_cols = arr.shape
    ranks = np.zeros(num_rows)
    dominated = np.zeros(num_rows, dtype=bool)

    for rank in range(num_rows):
        for i in range(num_rows):
            if dominated[i]:
                continue

            is_dominated = False

            for j in range(num_rows):
                if i == j or dominated[j]:
                    continue

                if np.all(arr[i] >= arr[j]) and np.any(arr[i] > arr[j]):
                    is_dominated = True
                    break

            if not is_dominated:
                ranks[i] = rank + 1
                dominated[i] = True
                break

    return ranks.astype(int)
