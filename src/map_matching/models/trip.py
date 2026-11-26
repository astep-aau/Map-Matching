from dataclasses import dataclass
from map_matching.models.gps_point import GpsPoint
from map_matching.models.trip_id import TripId

@dataclass(frozen=True, slots=True)
class Trip:
    id: TripId
    points: tuple[GpsPoint, ...]