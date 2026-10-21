from dataclasses import dataclass
from mapmatching.models.gpspoint import GpsPoint

@dataclass(frozen=True, slots=True)
class TripId:
    dataset: str
    taxi_id: str
    trajectory_id: str

@dataclass(frozen=True, slots=True)
class Trip:
    id: TripId
    points: tuple[GpsPoint, ...]