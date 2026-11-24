import os
import shutil

from fmm import Network, NetworkGraph

from mapmatching.repositories.road_segment_repository import RoadSegmentRepository

# Coordinate system in metres (UTM zone 50N) instead of degrees
NETWORK_CRS = 32650
NETWORK_FOLDER = f"/data/edges_{NETWORK_CRS}"
NETWORK_FILE = f"{NETWORK_FOLDER}/edges.shp"


def export_network(road_segments: RoadSegmentRepository) -> str:
    # If the file already exists in the cache, then return it
    if os.path.exists(NETWORK_FILE):
        return NETWORK_FILE

    # Use a temporary folder and delete any old one left from a failed export
    temporary = f"{NETWORK_FOLDER}_tmp"
    shutil.rmtree(temporary, ignore_errors=True)

    print(f"Exporting osm_edges to {NETWORK_FILE}")
    road_segments.export_to_shapefile(temporary, NETWORK_CRS)

    os.replace(temporary, NETWORK_FOLDER)
    return NETWORK_FILE


def load_network(road_segments: RoadSegmentRepository) -> tuple[Network, NetworkGraph]:
    # Loads the roads from the file into memory, so FMM can use them. Also a grid for fast lookups
    network = Network(export_network(road_segments), "id", "source", "target")

    # Builds the road graph - which roads are connected and what way you can drive them
    graph = NetworkGraph(network)

    print(f"Network loaded: {network.get_node_count()} nodes, {network.get_edge_count()} edges")
    return network, graph