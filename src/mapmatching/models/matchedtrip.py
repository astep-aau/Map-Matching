from dataclasses import dataclass, field
from typing import Literal

from mapmatching.models.trip import TripId

@dataclass(frozen=True, slots=True)
class MatchedTrip:
    trip_id: TripId                               # reuses the existing TripId
    algorithm: Literal["fmm", "stmatch"]
    status: Literal["matched", "failed"]
    road_points: tuple[int, ...] = ()             # matched edge ids (osm_edges.fid), in order
    params: dict = field(default_factory=dict)    # k, radius, gps_error, ...