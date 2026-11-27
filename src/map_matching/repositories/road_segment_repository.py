import os
import subprocess

from map_matching.models.road_segment import RoadSegment
from map_matching.models.coordinate import Coordinate
from map_matching.repositories.base_repository import BaseRepository

class RoadSegmentRepository(BaseRepository):

    def get_all(self) -> tuple[RoadSegment, ...]:
        #the sql query being run on the database
        rows = self.fetch("SELECT fid, u, v, length, highway, ST_AsText(geometry) FROM osm_edges ORDER BY fid")
        return tuple(self.convert_to_road_segment(row) for row in rows)

    #this is a helper function that converts the multiple amounts of coordinates given in a long string into coordinate objects
    def convert_coords(self, linestring: str) -> tuple[Coordinate, ...]:
        coordinates = []

        inner_str = linestring[linestring.index("(") + 1 : linestring.rindex(")")]

        for coordinate_pair in inner_str.split(","):
            lon, lat = coordinate_pair.split()
            coordinates.append(Coordinate(lon=float(lon), lat = float(lat)))
        return tuple(coordinates)

    def convert_to_road_segment(self, row: tuple) -> RoadSegment:
        return RoadSegment(
            id = row[0],
            source = row[1],
            target = row[2],
            length_m = row[3],
            highway = row[4],
            coordinates = self.convert_coords(row[5])
        )

    # Saves all the roads as a shapefile in metres, so FMM can read them
    def export_to_shapefile(self, folder: str, crs: int) -> None:
        info = self.connection.info
        database = f"PG:host={info.host} port={info.port} dbname={info.dbname} user={info.user}"
        query = f"SELECT fid AS id, u AS source, v AS target, ST_Transform(geometry, {crs}) AS geometry FROM osm_edges"

        subprocess.run(
            ["ogr2ogr", "-f", "ESRI Shapefile", folder, database, "-sql", query, "-nln", "edges", "-nlt", "LINESTRING"],
            check = True,
            env = {**os.environ, "PGPASSWORD": info.password},
        )

    def test_repository(self) -> str:
        count = self.fetch("SELECT count(*) FROM osm_edges")[0][0]
        first = self.convert_to_road_segment(self.fetch("SELECT fid, u, v, length, highway, ST_AsText(geometry) FROM osm_edges LIMIT 1")[0])
        return f"Road Segment Repository has {count} rows, this is the first one: {first}"

    def get_endpoints(self) -> dict[int, tuple[int, int]]:
        """finds origin id and destination id"""
        rows = self.fetch("SELECT fid, u, v FROM osm_edges")
        return {row[0]: (row[1], row[2]) for row in rows}
        