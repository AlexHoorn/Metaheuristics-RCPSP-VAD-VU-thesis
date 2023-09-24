import seaborn as sns
from pathlib import Path
import pickle
import random
from collections import defaultdict
from dataclasses import dataclass, field

import matplotlib.patches as patches
import networkx as nx
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from eaplanner.entities.assignment import Assignment
from eaplanner.entities.resource import Resource
from eaplanner.entities.constraint import (
    BaseConstraint,
    RelationConstraint,
    ResourceConstraint,
)
import csv


@dataclass
class Schedule:
    assignments: list[Assignment] = field(default_factory=list)
    constraints: list[BaseConstraint] = field(default_factory=list)

    def add_assignment(self, assignment: Assignment):
        self.assignments.append(assignment)

    def add_constraint(self, constraint: BaseConstraint):
        self.constraints.append(constraint)

    def get_total_makespan(self):
        if not self.assignments:
            return 0

        start = min(assignment.start for assignment in self.assignments)
        end = max(assignment.end for assignment in self.assignments)

        return end - start

    def get_start(self):
        return min(assignment.start for assignment in self.assignments)

    def get_end(self):
        return max(assignment.end for assignment in self.assignments)

    def get_total_penalty(self):
        return sum(constraint.get_penalty() for constraint in self.constraints)

    def get_assignment_by_id(self, id: int):
        return next(
            assignment for assignment in self.assignments if assignment.id == id
        )

    def reset_assignment_ids(self):
        for i, assignment in enumerate(sorted(self.assignments, key=lambda a: a.id)):
            assignment.id = i

    def remove_assignments_without_constraints(self):
        assignment_ids = set()
        for constraint in self.constraints:
            assignment_ids.update([a.id for a in constraint.get_assignments()])

        self.assignments = [a for a in self.assignments if a.id in assignment_ids]

    def repair_constraints(
        self, shuffle: bool = True, pct: float = 1.0, max_loops: int = 2
    ):
        constraints = self.constraints
        for _ in range(max_loops):
            # randomly select constraints
            constraints = [c for c in self.constraints if random.uniform(0, 1) <= pct]

            if shuffle:
                constraints = sorted(constraints, key=lambda _: random.random())

            # list comprehension to run all attempts
            if not any([c.attempt_repair() for c in constraints]):
                break

    def calculate_possible_combinations(self, duration: int | None = None):
        if duration is None:
            duration = self.get_total_makespan()

        try:
            return (duration * (duration - 1) / 2) ** len(self.assignments)
        except OverflowError:
            return float("inf")

    def get_constraint_per_group(self):
        groups: dict[str, list[BaseConstraint]] = defaultdict(list)
        for constraint in self.constraints:
            groups[type(constraint).__name__].append(constraint)

        return groups

    def get_total_hours_per_day(self):
        hours_per_day: dict[int, float] = defaultdict(float)
        for assignment in self.assignments:
            for day in range(assignment.start, assignment.end):
                hours_per_day[day] += assignment.hours_per_day

        return hours_per_day

    def as_graph(self):
        import networkx as nx

        G = nx.DiGraph()
        for assignment in self.assignments:
            G.add_node(
                assignment.id,
                start=assignment.start,
                duration=assignment.duration,
                hours=assignment.hours,
            )
        for constraint in self.constraints:
            if isinstance(constraint, RelationConstraint):
                G.add_edge(
                    constraint.predecessor.id,
                    constraint.successor.id,
                    penalty=constraint.get_penalty(),
                    label=constraint.type.short_name,
                )

        return G

    def visualize_graph(self, ax: Axes | None = None, show_edge_labels: bool = True):
        G = self.as_graph()

        if ax is None:
            _, ax = plt.subplots()

        pos = nx.nx_pydot.pydot_layout(G, prog="dot")
        penalties = list(nx.get_edge_attributes(G, "penalty").values())  # type: ignore
        hours = list(nx.get_node_attributes(G, "hours").values())  # type: ignore
        nx.draw(  # type: ignore
            G,
            pos,
            with_labels=True,
            edge_color=penalties,
            edge_cmap=plt.cm.RdYlGn_r,  # type: ignore
            node_color=hours,
            cmap=plt.cm.Reds,  # type: ignore
            ax=ax,
        )
        if show_edge_labels:
            nx.draw_networkx_edge_labels(  # type: ignore
                G,
                pos,
                edge_labels=nx.get_edge_attributes(G, "label"),  # type: ignore
                ax=ax,
            )

        return ax

    def visualize_gantt(
        self,
        ax: Axes | None = None,
        show_constraints: bool = True,
        show_legend: bool = False,
    ):
        if ax is None:
            _, ax = plt.subplots()

        ax.set_xlim(self.get_start() - 0.1, self.get_end() + 0.1)
        ax.set_ylim(0, max(assignment.id for assignment in self.assignments) + 1)

        for assignment in self.assignments:
            ax.add_patch(
                patches.Rectangle(
                    (assignment.start, assignment.id),
                    assignment.duration,
                    1,
                    linewidth=1,
                    zorder=1,
                )
            )

        if show_constraints:
            resource_constraints = [
                c for c in self.constraints if isinstance(c, ResourceConstraint)
            ]
            resource_colors = sns.color_palette(
                "colorblind", n_colors=len(resource_constraints)
            )
            for i, constraint in enumerate(resource_constraints):
                constraint.color = resource_colors[i]  # type: ignore
                # add to legend
                ax.add_patch(
                    patches.Rectangle(
                        (0, 0),
                        0,
                        0,
                        linewidth=1,
                        zorder=1,
                        label=constraint.resource.name,
                        color=constraint.color,
                    )
                )

            for constraint in self.constraints:
                ax = constraint.visualize_gantt(ax)

        # legend
        if show_legend:
            ax.legend()

        ax.set_xlabel("Day")
        ax.set_ylabel("Activity")
        ax.set_title("Gantt Chart")

        return ax

    def visualize_required_resources(self, ax: Axes | None = None, legend: bool = True):
        if ax is None:
            _, ax = plt.subplots()

        resources = [
            constraint
            for constraint in self.constraints
            if isinstance(constraint, ResourceConstraint)
        ]

        for resource in resources:
            daily_required_capacity = resource.get_daily_required_capacity()
            min_day = min(daily_required_capacity.keys())
            max_day = max(daily_required_capacity.keys())
            days = range(min_day, max_day + 1)
            capacity = [daily_required_capacity[day] for day in days]
            ax.plot(days, capacity, label=resource.resource.name)

        if legend:
            ax.legend()
        ax.set_xlabel("Day")
        ax.set_ylabel("Capacity")
        ax.set_title("Required capacity per resource")

        return ax

    def visualize_hours_per_day(self, ax: Axes | None = None):
        if ax is None:
            _, ax = plt.subplots()

        hours_per_day = self.get_total_hours_per_day()
        min_day = min(hours_per_day.keys())
        max_day = max(hours_per_day.keys())
        days = range(min_day, max_day + 1)
        hours = [hours_per_day[day] for day in days]
        ax.plot(days, hours)

        ax.set_xlabel("Day")
        ax.set_ylabel("Hours")
        ax.set_title("Hours per day")

        return ax

    def save(self, filename: Path):
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_bytes(pickle.dumps(self))

    def save_csv(self, filepath: Path):
        filepath.mkdir(parents=True, exist_ok=True)

        # write assignments
        with open(filepath / "activities.csv", "w+") as f:
            f.write("id,hours,start,duration\n")
            for assignment in self.assignments:
                f.write(assignment.to_csv_row() + "\n")

        # write relation constraints
        relation_constraints = [
            constraint
            for constraint in self.constraints
            if isinstance(constraint, RelationConstraint)
        ]
        with open(filepath / "sequence_constraints.csv", "w+") as f:
            f.write("predecessor_id,successor_id,type\n")
            for constraint in relation_constraints:
                f.write(constraint.to_csv_row() + "\n")

        # write resource constraints
        resource_constraints = [
            constraint
            for constraint in self.constraints
            if isinstance(constraint, ResourceConstraint)
        ]
        with open(filepath / "resource_constraints.csv", "w+") as f:
            f.write("resource_name,assignment_ids\n")
            for constraint in resource_constraints:
                f.write(constraint.to_csv_row() + "\n")

        # write resources
        resources = [c.resource for c in resource_constraints]
        with open(filepath / "resources.csv", "w+") as f:
            f.write("name,total_capacity\n")
            for resource in resources:
                f.write(resource.to_csv_row() + "\n")

    @staticmethod
    def load(filename: Path):
        if not filename.exists():
            raise FileNotFoundError(f"File {filename} does not exist")

        if filename.suffix == ".pkl":
            return Schedule.load_pickle(filename)

        return Schedule.load_csv(filename)

    @staticmethod
    def load_pickle(filename: Path):
        loaded = pickle.loads(filename.read_bytes())

        if not isinstance(loaded, Schedule):
            raise ValueError("File does not contain a Schedule object")

        return loaded

    @staticmethod
    def load_csv(filename: Path):
        assignments: list[Assignment] = []
        resources: list[Resource] = []
        constraints: list[BaseConstraint] = []

        with open(filename / "activities.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                assignments.append(Assignment.from_csv_row(row))

        with open(filename / "sequence_constraints.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                constraints.append(RelationConstraint.from_csv_row(row, assignments))

        with open(filename / "resources.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                resources.append(Resource.from_csv_row(row))

        with open(filename / "resource_constraints.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                constraints.append(
                    ResourceConstraint.from_csv_row(row, assignments, resources)
                )

        return Schedule(assignments=assignments, constraints=constraints)

    def __len__(self):
        return len(self.assignments)
