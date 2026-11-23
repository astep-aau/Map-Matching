import os
import shutil
import subprocess

from fmm import Network, NetworkGraph

from mapmatching.repositories.config import Settings

# Coordinate system in metres (UTM zone 50N) instead of degrees
NETWORK_CRS = 32650
NETWORK_FOLDER = f"/data/edges_{NETWORK_CRS}"
NETWORK_FILE = f"{NETWORK_FOLDER}/edges.shp"

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

    # Use a temporary folder and delete any old one left from a failed export
    temporary = f"{NETWORK_FOLDER}_tmp"
    shutil.rmtree(temporary, ignore_errors=True)

    # The database address, where we receive the data from
    database = f"PG:host={settings.db_host} port={settings.db_port} dbname={settings.db_name} user={settings.db_user}"

    print(f"Exporting osm_edges to {NETWORK_FILE}")

    # Runs ogr2ogr, which reads the roads from the database and writes them as a shapefile
    subprocess.run(
        ["ogr2ogr", "-f", "ESRI Shapefile", temporary, database,
         "-sql", EXPORT_SQL, "-nln", "edges", "-nlt", "LINESTRING"],
        check=True,
        env={**os.environ, "PGPASSWORD": settings.db_password},
    )
    os.replace(temporary, NETWORK_FOLDER)
    return NETWORK_FILE

def load_network(settings: Settings) -> tuple[Network, NetworkGraph]:
    # Loads the roads from the file into memory, so FMM can use them. Also a grid for fast lookups
    network = Network(export_network(settings), "id", "source", "target")
    
    # Builds the road graph - which roads are connected and what way you can drive them
    graph = NetworkGraph(network)

    print(f"Network loaded: {network.get_node_count()} nodes, {network.get_edge_count()} edges")
    return network, graph



    # Future dev - Single responsibility: Omskrive export_network funktionen til at benytte en repo der selv indhenter data.