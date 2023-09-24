import json
import pickle
import subprocess
from collections import OrderedDict
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1 import make_axes_locatable
from sklearn.decomposition import PCA
from tqdm import tqdm

from eaplanner.interpreter import ScheduleInterpreterBase
from eaplanner.utils import rank_lexicographic

DPI = 200

sns.set()


class ResultVisualization:
    logbook: pd.DataFrame
    solution_individual: list[int]
    solution_scores: dict[str, float]
    baseline_scores: dict[str, float]
    interpreter: ScheduleInterpreterBase
    population: pd.DataFrame | None = None

    def __init__(self, folder: Path):
        if not folder.exists():
            raise ValueError(f"Folder {folder} does not exist")

        self.folder = folder

        self.fig_folder = self.folder / "figures"
        self.fig_folder.mkdir(exist_ok=True)

        self.logbook = pd.read_csv(self.folder / "logbook.csv")

        solution = json.loads((self.folder / "solution.json").read_text())
        self.solution_individual = solution["individual"]
        self.solution_scores = solution["scores"]

        self.interpreter = pickle.loads((self.folder / "instance.pkl").read_bytes())

        self.baseline_scores = {
            k: v
            for k, v in zip(self.interpreter.score_names, self.interpreter.get_scores())
        }

        if (self.folder / "population.feather").exists():
            self.population = pd.read_feather(self.folder / "population.feather")

    @property
    def score_columns(self):
        return [f"score_{s}" for s in self.solution_scores]

    @staticmethod
    def _get_gene_columns(population: pd.DataFrame) -> list[str]:
        return [c for c in population.columns if c.startswith("gene_")]

    @classmethod
    def _get_start_columns(cls, population: pd.DataFrame) -> list[str]:
        return cls._get_gene_columns(population)[::2]

    @classmethod
    def _get_duration_columns(cls, population: pd.DataFrame) -> list[str]:
        return cls._get_gene_columns(population)[1::2]

    def visualize_convergence(self, x_axis: Literal["gen"] | Literal["nevals"] = "gen"):
        scores = list(self.solution_scores)
        fig, axes = plt.subplots(
            1, len(scores), figsize=(len(scores) * 6.4, 4.8), sharex=True
        )

        x = self.logbook[x_axis]
        if x_axis == "nevals":
            x = x.cumsum()

        for ax, score in zip(axes, scores):
            ax.fill_between(
                x,
                self.logbook[f"avg_{score}"] + self.logbook[f"std_{score}"],  # type: ignore
                self.logbook[f"avg_{score}"] - self.logbook[f"std_{score}"],  # type: ignore
                alpha=0.2,
                label="std",
            )
            ax.hlines(
                y=self.baseline_scores[score],
                xmin=x.min(),
                xmax=x.max(),
                label="baseline",
                color="k",
                linestyle="--",
            )
            ax.plot(
                x, self.logbook[f"min_{score}"], label="min", color="g", linestyle="--"
            )
            ax.plot(x, self.logbook[f"avg_{score}"], label="mean", color="b")
            ax.plot(
                x, self.logbook[f"max_{score}"], label="max", color="r", linestyle="--"
            )
            ax.legend()
            ax.set_xlabel("Generation" if x_axis == "gen" else "Evaluations")
            ax.set_ylabel(score.title())
            ax.set_title(
                f"{score.title()} over generations, final={self.solution_scores[score]:0.2f}"
            )

        fig.tight_layout()

        fig.savefig(str(self.fig_folder / f"fitness_{x_axis}.png"), dpi=DPI)
        fig.savefig(str(self.fig_folder / f"fitness_{x_axis}.svg"))

        fig.clf()
        plt.close(fig)

    def visualize_solution(self, show_gantt_constraints: bool = True):
        self.interpreter.interpret(np.array(self.solution_individual))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(2 * 6.4, 4.8))
        self.interpreter.schedule.visualize_gantt(
            ax1, show_constraints=show_gantt_constraints
        )
        self.interpreter.schedule.visualize_required_resources(ax2)

        fig.suptitle(
            "Solution, "
            + ", ".join(f"{k}={v:0.2f}" for k, v in self.solution_scores.items())
        )

        fig.tight_layout()
        fig.savefig(str(self.fig_folder / "solution.png"), dpi=DPI)
        fig.savefig(str(self.fig_folder / "solution.svg"))

        fig.clf()
        plt.close(fig)

    def visualize_generations_pca(self):
        if self.population is None:
            raise ValueError("Population is not available")
        
        pca = PCA(n_components=2, random_state=42)
        decomp = pca.fit_transform(
            self.population[self._get_gene_columns(self.population)]
        )

        fig, ax = plt.subplots()

        sns.scatterplot(
            x=decomp[:, 0],
            y=decomp[:, 1],
            hue=self.population["gen"],
            ax=ax,
            palette="viridis",
            hue_order=self.population["gen"].unique().sort(),
            s=3,
        )

        ax.set_xlabel("PC 1")
        ax.set_ylabel("PC 2")
        ax.set_title("Population PCA")

        fig.tight_layout()
        fig.savefig(str(self.fig_folder / "generations_pca.png"), dpi=DPI)
        fig.savefig(str(self.fig_folder / "generations_pca.svg"))

        fig.clf()
        plt.close(fig)

    def visualize_generations_pca_video(self, sample_every: int = 1):
        if self.population is None:
            raise ValueError("Population is not available")
        
        ngens = self.population["gen"].max()
        indexes = list(range(0, ngens, sample_every)) + [ngens - 1]

        generations = {i: self.population[self.population["gen"] == i] for i in indexes}
        generations: dict[int, pd.DataFrame] = OrderedDict(sorted(generations.items()))

        pca = PCA(n_components=2, random_state=42)
        decomp = pca.fit_transform(
            pd.concat(generations.values())[self._get_gene_columns(generations[0])]
        )

        xlim = (decomp[:, 0].min(), decomp[:, 0].max())
        ylim = (decomp[:, 1].min(), decomp[:, 1].max())
        folder = self.fig_folder / "pca"

        for i, (gen, pop) in tqdm(
            enumerate(generations.items()),
            desc="Rendering frames",
            total=len(generations),
        ):
            fig = self._render_pca_frame(gen, pop, pca, xlim, ylim)
            folder.mkdir(exist_ok=True)
            fig.savefig(str(folder / f"{i}.png"), dpi=DPI)
            fig.clf()
            plt.close(fig)

        subprocess.run(
            "ffmpeg -y -r 6 -i pca/%d.png pca.mp4",
            cwd=self.fig_folder,
            shell=True,
        )

    def _render_pca_frame(self, gen, population, pca, xlim, ylim):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)  # type: ignore

        decomp = pca.transform(population[self._get_gene_columns(population)])
        ranks = rank_lexicographic(
            population[[f"score_{s}" for s in self.solution_scores]].to_numpy()
        )
        ax.scatter(x=decomp[:, 0], y=decomp[:, 1], c=ranks, cmap="RdYlGn_r", s=3)
        ax.set_title(f"Decomposition of population ({gen=})")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")

        divided = make_axes_locatable(ax)
        cax = divided.append_axes("right", size="5%", pad=0)
        plt.colorbar(
            ax.collections[0],  # type: ignore
            cax=cax,
            ticks=[ranks.min(), ranks.max()],
        )

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)  # type: ignore

        fig.tight_layout()
        return fig

    def visualize_generations_video(
        self, show_gantt_constraints: bool = True, sample_every: int = 1
    ):
        if self.population is None:
            raise ValueError("Population is not available")
        
        ngens = self.population["gen"].max()
        indexes = list(range(0, ngens, sample_every)) + [ngens - 1]

        generations = {i: self.population[self.population["gen"] == i] for i in indexes}
        generations: dict[int, pd.DataFrame] = OrderedDict(sorted(generations.items()))

        pca = PCA(n_components=2, random_state=42)
        decomp = pca.fit_transform(
            pd.concat(generations.values())[self._get_gene_columns(generations[0])]
        )
        xlim = (decomp[:, 0].min(), decomp[:, 0].max())
        ylim = (decomp[:, 1].min(), decomp[:, 1].max())

        out_dir = self.fig_folder / "population"
        out_dir.mkdir(parents=True, exist_ok=True)

        for i, (gen, pop) in tqdm(
            enumerate(generations.items()),
            desc="Rendering frames",
            total=len(generations),
        ):
            fig = self._render_population_frame(
                gen, pop, pca, xlim, ylim, show_gantt_constraints=show_gantt_constraints
            )

            fig.savefig(str(out_dir / f"{i}.png"), dpi=DPI)
            fig.clf()
            plt.close(fig)

        subprocess.run(
            "ffmpeg -y -r 6 -i population/%d.png evolution.mp4",
            cwd=self.fig_folder,
            shell=True,
        )

    def _render_population_frame(
        self,
        gen: int,
        population: pd.DataFrame,
        pca: PCA,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        show_gantt_constraints: bool = True,
    ):
        best = population.sort_values(self.score_columns).iloc[0]
        best_individual = best[self._get_gene_columns(population)].to_numpy()

        fig = plt.figure(figsize=(2 * 6.4, 4.8 * 2), constrained_layout=True)

        fig.suptitle(
            f"Generation {gen}, fitness: "
            + ", ".join(
                f"{c.replace('score_','')}={best[c]:0.2f}" for c in self.score_columns
            )
        )

        gs = fig.add_gridspec(2, 6)
        ax_gantt = fig.add_subplot(gs[0, :3])  # type: ignore
        ax_resources = fig.add_subplot(gs[0, 3:])  # type: ignore
        ax_pca = fig.add_subplot(gs[1, :2])  # type: ignore
        ax_dist_start = fig.add_subplot(gs[1, 2:4])  # type: ignore
        ax_dist_duration = fig.add_subplot(gs[1, 4:])  # type: ignore

        self.interpreter.interpret(best_individual)
        ax_gantt = self.interpreter.schedule.visualize_gantt(
            ax_gantt, show_constraints=show_gantt_constraints
        )
        ax_resources = self.interpreter.schedule.visualize_required_resources(
            ax_resources
        )

        ax_pca = self._visualize_population_pca(ax_pca, population, pca)
        if xlim is not None:
            ax_pca.set_xlim(xlim)
        if ylim is not None:
            ax_pca.set_ylim(ylim)  # type: ignore

        n_assignments = len(best_individual) // 2
        ax_dist_start, ax_dist_duration = self._visualize_population_distribution(
            ax_dist_start, ax_dist_duration, n_assignments, population
        )

        return fig

    def _visualize_population_pca(self, ax: Axes, population: pd.DataFrame, pca: PCA):
        decomp = pca.transform(population[self._get_gene_columns(population)])
        ranks = rank_lexicographic(
            population[[f"score_{s}" for s in self.solution_scores]].to_numpy()
        )
        min_pop_fitness = ranks.min()
        max_pop_fitness = ranks.max()
        ax.scatter(x=decomp[:, 0], y=decomp[:, 1], c=ranks, cmap="RdYlGn_r", s=3)
        ax.set_title("Decomposition of population")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")

        divided = make_axes_locatable(ax)
        cax = divided.append_axes("right", size="5%", pad=0)
        plt.colorbar(
            ax.collections[0],  # type: ignore
            cax=cax,
            ticks=[min_pop_fitness, max_pop_fitness],
        )

        return ax

    def _visualize_population_distribution(
        self,
        ax_start: Axes,
        ax_duration: Axes,
        n_assignments: int,
        population: pd.DataFrame,
    ):
        pop_array = population[self._get_gene_columns(population)].to_numpy().flatten()
        starts = pop_array[::2]
        durations = pop_array[1::2]

        assignments = np.tile(np.arange(n_assignments), len(starts) // n_assignments)

        ax_start = sns.boxenplot(
            x=starts,
            y=assignments,
            ax=ax_start,
            orient="h",
            color="C0",
            showfliers=False,
            linewidth=1,
        )
        ax_start.set_title("Start times")
        ax_start.set_xlabel("Day")
        ax_start.set_ylabel("Activity")
        ax_start.invert_yaxis()

        ax_duration = sns.boxenplot(
            x=durations,
            y=assignments,
            ax=ax_duration,
            orient="h",
            color="C1",
            showfliers=False,
            linewidth=1,
        )
        ax_duration.set_title("Durations")
        ax_duration.set_xlabel("Day")
        ax_duration.set_ylabel("Activity")
        ax_duration.invert_yaxis()

        return ax_start, ax_duration

    def visualize_fitnesses(self, f1: str = "penalty", f2: str = "makespan"):
        if self.population is None:
            raise ValueError("Population is not available")
        
        fig, ax = plt.subplots()

        sns.scatterplot(
            x=self.population[f"score_{f1}"],
            y=self.population[f"score_{f2}"],
            hue=self.population["gen"],
            ax=ax,
            palette="viridis",
            hue_order=self.population["gen"].unique().sort(),
            s=3,
        )

        ax.set_xlabel(f1.capitalize())
        ax.set_ylabel(f2.capitalize())
        ax.set_title("Fitness over generations")

        fig.tight_layout()
        fig.savefig(str(self.fig_folder / "generations_fitness.png"), dpi=DPI)
        fig.savefig(str(self.fig_folder / "generations_fitness.svg"))

        fig.clf()
        plt.close(fig)
