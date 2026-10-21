from dataclasses import dataclass
from mapmatching.models.coordinate import Coordinate

@dataclass(frozen=True, slots=True)
class RoadSegment:
    id: int
    source: int
    target: int
    length_m: float
    coordinates: tuple[Coordinate, ...]
    highway: str | None = None
    max_speed_kmh: float | None = None