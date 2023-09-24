from pathlib import Path
import seaborn as sns
from eaplanner.visualization import ResultVisualization
from multiprocessing import Pool
import os
import re


def visualize_all(path: Path):
    visualizer = ResultVisualization(path)

    visualizer.visualize_convergence(x_axis="gen")
    visualizer.visualize_convergence(x_axis="nevals")
    # visualizer.visualize_solution(show_gantt_constraints=True)
    # visualizer.visualize_generations_pca()
    # visualizer.visualize_fitnesses()
    # visualizer.visualize_generations_video(show_gantt_constraints=True, sample_every=15)
    # visualizer.visualize_generations_pca_video(sample_every=15)

    return 1


if __name__ == "__main__":
    pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}"
    paths = [
        Path(x[0]) for x in os.walk(".") if re.match(pattern, os.path.basename(x[0]))
    ]

    sns.set()

    with Pool() as pool:
        pool.map(visualize_all, paths)
