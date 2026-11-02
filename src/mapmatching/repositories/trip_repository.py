from mapmatching.repositories.base_repository import BaseRepository

from mapmatching.models.trip import Trip, TripId
from mapmatching.models.coordinate import Coordinate
from mapmatching.models.gpspoint import GpsPoint




class TripRepository(BaseRepository):

    def count_trips(self) -> int:
        rows = self.fetch("SELECT count(*) FROM trajectories")
        return rows[0][0]

    def get_batch(self, batch_number: int, batch_size: int) -> tuple[Trip, ...]:
            rows = self.fetch("SELECT dataset, taxi_id, trajectory_id, gps_points FROM trajectories "
                              "ORDER BY dataset, taxi_id, trajectory_id "
                              "LIMIT %s OFFSET %s",
                              (batch_size, batch_number * batch_size),
                              )
            return tuple(self.convert_to_trip(row) for row in rows)
    
    def get_all(self) -> tuple[Trip, ...]:
        rows = self.fetch("SELECT dataset, taxi_id, trajectory_id, gps_points FROM trajectories")
        return tuple(self.convert_to_trip(row) for row in rows)

    def convert_to_trip(self, row: tuple) -> Trip:
        return Trip(
            id = TripId(dataset=row[0], taxi_id=row[1], trajectory_id=row[2]),
            points=tuple(self.convert_to_gps_point(p) for p in row[3]),
        )

    def convert_to_gps_point(self, row: tuple) -> GpsPoint:
        return GpsPoint(
            coordinate=Coordinate(lon=row[2],lat=row[3]),
            timestamp=row[1],
        )