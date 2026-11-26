from dataclasses import dataclass
from map_matching.models.coordinate import Coordinate

@dataclass(frozen=True, slots=True)
class GpsPoint:
    coordinate: Coordinate
    timestamp: float #Unix seconds