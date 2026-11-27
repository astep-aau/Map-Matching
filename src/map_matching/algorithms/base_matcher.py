from abc import ABC, abstractmethod

from pyproj import Transformer

from map_matching.algorithms.network import NETWORK_CRS
from map_matching.models.matched_trip import MatchedTrip
from map_matching.models.trip import Trip

# Converts GPS points from degrees to the same metres as the road network
TO_METRES = Transformer.from_crs(4326, NETWORK_CRS, always_xy=True)

# The GPS points as a line in metres, the input format STmatch uses
def trip_to_wkt(trip: Trip) -> str:
    lons = [point.coordinate.lon for point in trip.points]
    lats = [point.coordinate.lat for point in trip.points]
    xs, ys = TO_METRES.transform(lons, lats)
    points = ", ".join(f"{x} {y}" for x, y in zip(xs, ys))
    return f"LINESTRING({points})"

class BaseMatcher(ABC):
    # Each algorithm sets its own name: "fmm" or "stmatch"
    algorithm: str

    # Constructor for initialising the parameters
    def __init__(self, params: dict, edge_endpoints: dict[int, tuple[int, int]]):
        self.params = params
        self.edge_endpoints = edge_endpoints

    # A trip needs at least two GPS points to have a route
    def match_trip(self, trip: Trip) -> MatchedTrip:
        edge_ids: list[int] = []

        origin = destination = None
        if len(trip.points) >= 2:
            try:
                edge_ids = self.find_edges(trip)
                if edge_ids:
                    origin = self.edge_endpoints[edge_ids[0]][0]
                    destination = self.edge_endpoints[edge_ids[-1]][1]
            except Exception as error:
                print(f"Trip {trip.id.trajectory_id} failed: {error}")
                edge_ids, origin, destination = [], None, None

        # No roads found means the match failed
        status = "matched" if edge_ids else "failed"
        return MatchedTrip(trip.id, self.algorithm, status, tuple(edge_ids), self.params, origin_node_id = origin, destination_node_id = destination)

    # Each algorithm writes its own version
    @abstractmethod
    def find_edges(self, trip: Trip) -> list[int]:
        ...