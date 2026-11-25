from mapmatching.algorithms.base_matcher import trip_to_wkt, BaseMatcher

from mapmatching.models.trip import Trip

from fmm import FastMapMatch, FastMapMatchConfig

class FmmMatcher(BaseMatcher):
    algorithm = "fmm"

    
    def __init__(self, network, graph, ubodt, params: dict):
        super().__init__(params)
        self.network = network
        self.graph = graph
        self.ubodt = ubodt

        self.model = FastMapMatch(network, graph, ubodt)
        self.config = FastMapMatchConfig(params["k"], params["radius"], params["gps_error"])

    def find_edges(self, trip):
        return list(self.model.match_wkt(trip_to_wkt(trip), self.config).cpath)