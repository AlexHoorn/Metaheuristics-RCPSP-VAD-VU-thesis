from dataclasses import dataclass


@dataclass
class Resource:
    name: str
    min_capacity: float = 0
    med_capacity: float = 0
    # if day is None, then the resource applies to all days
    # but this may be overwritten by a resource constraint with a specific day
    day: int | None = None

    def __post_init__(self):
        self.total_capacity = self.min_capacity + self.med_capacity

    def to_csv_row(self):
        return ",".join(
            str(v)
            for v in [
                self.name,
                self.total_capacity,
            ]
        )

    @staticmethod
    def from_csv_row(row: dict[str, str]):
        return Resource(
            name=row["name"],
            min_capacity=float(row["total_capacity"]),
        )
