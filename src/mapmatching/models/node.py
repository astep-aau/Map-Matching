from dataclasses import dataclass

from mapmatching.models.coordinate import Coordinate

@dataclass(frozen=True, slots=True)
class Node:
    id: int
    coordinate: Coordinate