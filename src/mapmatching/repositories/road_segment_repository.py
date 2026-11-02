from mapmatching.models.roadsegment import RoadSegment
from mapmatching.models.coordinate import Coordinate
from mapmatching.repositories.base_repository import BaseRepository

class RoadSegmentRepository(BaseRepository):

    def get_all(self) -> tuple[RoadSegment, ...]:
        #the sql query being run on the database
        rows = self.fetch("SELECT fid, u, v, length, highway, ST_AsText(geometry) FROM osm_edges ORDER BY fid")
        return tuple(self.convert_to_roadsegment(row) for row in rows)



    #this is a helper function that converts the multiple amounts of coordinates given in a long string into coordinate objects
    def convert_coords(self, linestring: str) -> tuple[Coordinate, ...]:
        coordinates = []

        innerStr = linestring[linestring.index("(") + 1 : linestring.rindex(")")]

        for coordPair in innerStr.split(","):
            lon, lat = coordPair.split()
            coordinates.append(Coordinate(lon=float(lon), lat = float(lat)))
        return tuple(coordinates)



    def convert_to_roadsegment(self, row: tuple) -> RoadSegment:
        return RoadSegment(
            id=row[0],
            source=row[1],
            target=row[2],
            length_m=row[3],
            highway=row[4],
            coordinates=self.convert_coords(row[5])
        )

    def test_repo(self) -> str:
             count = self.fetch("SELECT count(*) FROM osm_edges")[0][0]
             first = self.convert_to_roadsegment(self.fetch("SELECT fid, u, v, length, highway, ST_AsText(geometry) FROM osm_edges LIMIT 1")[0])
             return f"Road Segment Repository has {count} rows, this is the first one: {first}"