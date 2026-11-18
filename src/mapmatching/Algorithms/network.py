import os
import subprocess

from fmm import Network, NetworkGraph

from mapmatching.repositories.config import Settings

# Coordinate system in metres (UTM zone 50N) instead of degrees
NETWORK_CRS = 32650
NETWORK_FILE = f"/data/edges_{NETWORK_CRS}.gpkg"

# SQL query ogr2ogr uses to get the roads (id, source, target, geometry in metres)
EXPORT_SQL = f"""
    SELECT fid AS id, u AS source, v AS target,
    ST_Transform(geometry, {NETWORK_CRS}) AS geometry
    FROM osm_edges
"""

def export_network(settings: Settings) -> str:
    # If the file already exists in the cache, then return it
    if os.path.exists(NETWORK_FILE):
        return NETWORK_FILE

    # Use a temporary file and delete any old one left from a failed export
    temporary = NETWORK_FILE.replace(".gpkg", ".tmp.gpkg")
    if os.path.exists(temporary):
        os.remove(temporary)

    # The database address, where we receive the data from
    database = f"PG:host={settings.db_host} port={settings.db_port} dbname={settings.db_name} user={settings.db_user}"

    print(f"Exporting osm_edges to {NETWORK_FILE}")

    # Runs ogr2ogr, which reads the roads from the database and writes them to the gpkg file
    subprocess.run(
        ["ogr2ogr", "-f", "GPKG", temporary, database, "-sql", EXPORT_SQL, "-nln", "edges"],
        check=True,
        env={**os.environ, "PGPASSWORD": settings.db_password},
    )
    os.replace(temporary, NETWORK_FILE)
    return NETWORK_FILE

def load_network(settings: Settings) -> tuple[Network, NetworkGraph]:
    # Loads the roads from the file into memory, so FMM can use them. Also a grid for fast lookups
    network = Network(export_network(settings), "id", "source", "target")
    
    # Builds the road graph - which roads are connected and what way you can drive them
    graph = NetworkGraph(network)

    print(f"Network loaded: {network.get_node_count()} nodes, {network.get_edge_count()} edges")
    return network, graph