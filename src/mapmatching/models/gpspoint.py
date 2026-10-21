from dataclasses import dataclass
from mapmatching.models.coordinate import Coordinate

@dataclass(frozen=True, slots=True)
class GpsPoint:
    coordinate: Coordinate
    timestamp: float #Unix seconds