import json
import os
from pathlib import Path
import re
from typing import Any
from eaplanner.entities.constraint import (
    DateConstraint,
    RelationConstraint,
    ResourceConstraint,
)

from eaplanner.interpreter import ScheduleInterpreterBase
import numpy as np
import pandas as pd

# find all subdirectories matching the pattern year-month-day_hour-minute-second
# e.g. 2021-03-01_15-00-00
pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}"
# pattern = r"\d{4}-\d{2}-\d{2}_\d.*"
subdirs = [
    Path(x[0]) for x in os.walk("results") if re.match(pattern, os.path.basename(x[0]))
]

data: list[dict[str, Any]] = []
for dir in subdirs:
    if not os.listdir(dir):
        os.rmdir(dir)
        continue

    if not Path(f"{dir}/solution.json").exists():
        continue

    instance_data: dict[str, Any] = {}

    if Path(f"{dir}/instance.pkl").exists():
        # Python instance
        interpreter = ScheduleInterpreterBase.load(dir / "instance.pkl")
        schedule = interpreter.schedule

        instance_data["assignments"] = len(schedule.assignments)
        instance_data["constraints"] = len(schedule.constraints)
        instance_data["relation_constraints"] = len(
            [c for c in schedule.constraints if isinstance(c, RelationConstraint)]
        )
        instance_data["resource_constraints"] = len(
            [c for c in schedule.constraints if isinstance(c, ResourceConstraint)]
        )
        instance_data["date_constraints"] = len(
            [c for c in schedule.constraints if isinstance(c, DateConstraint)]
        )
        instance_data["original_penalty"] = schedule.get_total_penalty()
        instance_data["original_makespan"] = schedule.get_total_makespan()

        solution: list[float] = json.loads(Path(f"{dir}/solution.json").read_text())[
            "individual"
        ]
        interpreter.interpret(np.array(solution))

        instance_data["solution_penalty"] = schedule.get_total_penalty()
        instance_data["solution_makespan"] = schedule.get_total_makespan()

        parameters: dict[str, float] = {}
        for p in re.findall(r"\((.*?)\)", dir.name)[0].split(", "):
            key, value = p.split("=")
            try:
                parameters[key] = float(value)
            except ValueError:
                parameters[key] = value

    elif Path(f"{dir}/instance").exists():
        # Rust instance
        instance_data["assignments"] = (
            sum(1 for line in open(f"{dir}/instance/activities.csv")) - 1
        )
        instance_data["relation_constraints"] = (
            sum(1 for line in open(f"{dir}/instance/sequence_constraints.csv")) - 1
        )
        instance_data["resource_constraints"] = (
            sum(1 for line in open(f"{dir}/instance/resource_constraints.csv")) - 1
        )
        instance_data["date_constraints"] = 0
        instance_data["constraints"] = (
            instance_data["relation_constraints"]
            + instance_data["resource_constraints"]
        )

        solution_json: dict[str, Any] = json.loads(
            Path(f"{dir}/solution.json").read_text()
        )

        instance_data["original_penalty"] = solution_json["original_scores"]["penalty"]
        instance_data["original_makespan"] = solution_json["original_scores"][
            "makespan"
        ]

        instance_data["solution_penalty"] = solution_json["scores"]["penalty"]
        instance_data["solution_makespan"] = solution_json["scores"]["makespan"]

    else:
        continue

    algorithm: str = re.findall(f"{pattern}_(.*?)\\(", dir.name)[0]
    instance_data["algorithm"] = algorithm
    data.append(instance_data)

df = pd.DataFrame(data)
df.to_csv("results.csv", index=False)
