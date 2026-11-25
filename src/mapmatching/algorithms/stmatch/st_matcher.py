from fmm import STMATCH, STMATCHConfig, Network, NetworkGraph, Trajectory, wkt2linestring

from mapmatching.algorithms.base_matcher import trip_to_wkt, BaseMatcher
from mapmatching.models.trip import Trip


class STmatcher(BaseMatcher):
    algorithm = "stmatch"

    def __init__(self, network: Network, graph: NetworkGraph, params: dict):
         
        super().__init__(params)
        self.model = STMATCH(network, graph)
        self.config = STMATCHConfig(params["k"], params["radius"], params["gps_error"], params["vmax"], params["factor"])
     
    def find_edges(self, trip: Trip) -> list[int]:
            # The GPS points as a line in metres, and the time of each point
            line = wkt2linestring(trip_to_wkt(trip))
            timestamps = [float(point.timestamp) for point in trip.points]

            # Return the most likely route between the GPS points
            return list(self.model.match_traj(Trajectory(0, line, timestamps), self.config).cpath)
