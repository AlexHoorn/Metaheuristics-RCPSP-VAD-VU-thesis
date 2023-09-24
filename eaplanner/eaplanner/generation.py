import math
import random
from typing import Literal

import networkx as nx
import numpy as np

from eaplanner.entities.assignment import Assignment
from eaplanner.entities.constraint import (
    DateConstraint,
    RelationConstraint,
    ResourceConstraint,
)
from eaplanner.entities.enum import DateType, RelationType
from eaplanner.entities.resource import Resource
from eaplanner.entities.schedule import Schedule


class ScheduleGenerator:
    @classmethod
    def generate_random_schedule(
        cls,
        n_assignments: int,
        k: int = 2,
        n_resources: int | Literal["auto"] = "auto",
        p_date: float = 0.16,
        mu_hours: float = 50,
        std_hours: float = 150,
        mu_resources: float = 100,
        std_resources: float = 30,
        seed: int | None = None,
    ):
        if seed is not None:
            random.seed(seed)

        G = cls.generate_schedule_graph(n_assignments, k, seed)
        G = cls.sort_graph_nodes(G)

        schedule = Schedule()
        cls.add_assignments_to_schedule(mu_hours, std_hours, G, schedule)
        cls.add_relations_to_schedule(G, schedule)

        schedule.assignments.sort(key=lambda assignment: assignment.id)

        for _ in range(10):
            if schedule.get_total_penalty() == 0:
                break

            schedule.repair_constraints(max_loops=100)
            cls.flip_invalid_relations(schedule)

        cls.remove_invalid_relations(schedule)
        cls.reset_assignments_starts(schedule)
        cls.add_dates_to_schedule(schedule, p_date)

        if n_resources == "auto" or n_resources > 0:
            cls.generate_resources_for_schedule(
                mu_resources, std_resources, schedule, n_resources
            )

        cls.remove_empty_constraints(schedule)

        return schedule

    @staticmethod
    def sort_graph_nodes(G: nx.DiGraph) -> nx.DiGraph:
        sorted_nodes = list(nx.lexicographical_topological_sort(G))  # type: ignore
        mapping = {node: i for i, node in enumerate(sorted_nodes)}
        G = nx.relabel_nodes(G, mapping)  # type: ignore
        return G

    @staticmethod
    def reset_assignments_starts(schedule):
        start = min(assignment.start for assignment in schedule.assignments)
        for assignment in schedule.assignments:
            assignment.start -= start

    @staticmethod
    def flip_invalid_relations(schedule: Schedule):
        n = 0
        for constraint in schedule.constraints:
            if (
                isinstance(constraint, RelationConstraint)
                and constraint.get_penalty() > 0
            ):
                constraint.predecessor, constraint.successor = (
                    constraint.successor,
                    constraint.predecessor,
                )
                n += 1

    @staticmethod
    def remove_invalid_relations(schedule: Schedule):
        n = 0
        for i, constraint in enumerate(schedule.constraints):
            if (
                isinstance(constraint, RelationConstraint)
                and constraint.get_penalty() > 0
            ):
                schedule.constraints.pop(i)
                n += 1

    @staticmethod
    def add_dates_to_schedule(
        schedule: Schedule,
        p_date: float = 0.16,
        weights=[0.0, 0.89, 0.09, 0.01, 0.0, 0.0, 0.0, 0.0],
    ):
        for assignment in schedule.assignments:
            if random.random() < p_date:
                constraint = DateConstraint(
                    DateType(np.random.choice(range(len(DateType)), p=weights)),
                    assignment,
                    0,
                )
                day = constraint.get_constraint_day()
                constraint.day = day
                schedule.add_constraint(constraint)

    @staticmethod
    def generate_resources_for_schedule(
        mu_hours: float,
        std_hours: float,
        schedule: Schedule,
        n_resources: int | Literal["auto"] = "auto",
    ):
        if n_resources == "auto":
            # params obtained from log regression
            n_resources = ScheduleGenerator.calculate_n_resources(schedule)

        random.shuffle(schedule.assignments)
        chunks = np.array_split(np.asarray(schedule.assignments), n_resources)

        for i, chunk in enumerate(chunks):
            resource = Resource(
                name=f"Resource {i}",
                min_capacity=max(1, math.ceil(random.gauss(mu_hours, std_hours))),
            )
            constraint = ResourceConstraint(
                resource,
                list(chunk),
            )
            schedule.add_constraint(constraint)

        schedule.assignments.sort(key=lambda assignment: assignment.id)

    @staticmethod
    def calculate_n_resources(schedule):
        return max(1, math.ceil(2.55 * math.log(len(schedule)) + 0.11))

    @staticmethod
    def add_assignments_to_schedule(
        mu_hours: float, std_hours: float, G: nx.DiGraph, schedule: Schedule
    ):
        for node in G.nodes:
            hours = max(1, int(np.random.chisquare(df=1) * std_hours + mu_hours))
            assignment = Assignment(id=node, hours=hours)
            assignment.duration = hours // 10
            schedule.add_assignment(assignment)

    @staticmethod
    def add_relations_to_schedule(
        G: nx.DiGraph, schedule: Schedule, p_rel: list[float] = [0.09, 0.73, 0.0, 0.18]
    ):
        for edge in G.edges:
            predecessor = schedule.get_assignment_by_id(edge[0])
            successor = schedule.get_assignment_by_id(edge[1])
            schedule.add_constraint(
                RelationConstraint(
                    RelationType(np.random.choice(range(len(RelationType)), p=p_rel)),
                    predecessor,
                    successor,
                )
            )

    @classmethod
    def generate_schedule_graph(
        cls, n_assignments: int, k: int, seed: int | None = None
    ) -> nx.DiGraph:
        # on average every assignment will be connected to k other assignments
        p_edge = max(0, k / (n_assignments - 1))
        G = nx.generators.random_graphs.binomial_graph(
            n=n_assignments, p=p_edge, seed=seed, directed=True
        )

        cls.remove_cycles(G)
        G = nx.algorithms.dag.transitive_reduction(G)

        if k == 0:
            return G

        for isolated_node in nx.isolates(G):  # type: ignore
            selected_node = random.sample([n for n in G.nodes], 1)[0]
            if selected_node != isolated_node:
                G.add_edge(isolated_node, selected_node)

        return G
    
    @staticmethod
    def remove_empty_constraints(schedule: Schedule):
        to_remove = []
        for constraint in schedule.constraints:
            if constraint.is_empty():
                to_remove.append(constraint)
                
        for constraint in to_remove:
            schedule.constraints.remove(constraint)

    @staticmethod
    def remove_cycles(G):
        while True:
            try:
                cycles = nx.algorithms.cycles.find_cycle(G)
            except nx.exception.NetworkXNoCycle:
                break
            else:
                G.remove_edges_from(cycles)
