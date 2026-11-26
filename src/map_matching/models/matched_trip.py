from dataclasses import dataclass, field
from typing import Literal

from map_matching.models.trip_id import TripId

@dataclass(frozen=True, slots=True)
class MatchedTrip:
    trip_id: TripId                               
    algorithm: Literal["fmm", "stmatch"]
    status: Literal["matched", "failed"]
    road_points: tuple[int, ...] = ()             
    params: dict = field(default_factory=dict)    