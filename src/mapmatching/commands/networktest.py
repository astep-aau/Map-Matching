from mapmatching.algorithms.network import load_network
from mapmatching.repositories.config import Settings
from mapmatching.repositories.connection import connect
from mapmatching.repositories.road_segment_repository import RoadSegmentRepository


def networktest() -> None:
    connection = connect(Settings.load_env_info())
    try:
        network, graph = load_network(RoadSegmentRepository(connection))

        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM osm_edges")
            expected = cursor.fetchone()[0]
    finally:
        connection.close()

    if network.get_edge_count() == expected:
        print(f"OK: all {expected} edges from osm_edges were loaded into FMM")
    else:
        print(f"FAILED: osm_edges has {expected} edges, but FMM loaded {network.get_edge_count()}")