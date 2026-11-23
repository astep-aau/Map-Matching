from mapmatching.algorithms.network import load_network
from mapmatching.repositories.config import Settings
from mapmatching.repositories.connection import connect


def networktest() -> None:
    settings = Settings.load_env_info()
    network, graph = load_network(settings)

    connection = connect(settings)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM osm_edges")
            expected = cursor.fetchone()[0]
    finally:
        connection.close()

    if network.get_edge_count() == expected:
        print(f"OK: all {expected} edges from osm_edges were loaded into FMM")
    else:
        print(f"FAILED: osm_edges has {expected} edges, but FMM loaded {network.get_edge_count()}")