from psycopg.types.json import Jsonb

from mapmatching.models.matchedtrip import MatchedTrip
from mapmatching.repositories.base_repository import BaseRepository


class MatchedTripRepository(BaseRepository):

    INSERT_SQL = (
        "INSERT INTO map_matching.matched_trajectories "
        "(dataset, taxi_id, trajectory_id, algorithm, status, road_points, params) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) "
        "ON CONFLICT (dataset, taxi_id, trajectory_id, algorithm) DO UPDATE SET "
        "status = EXCLUDED.status, "
        "road_points = EXCLUDED.road_points, "
        "params = EXCLUDED.params, "
        "matched_at = now()"
    )


    def save_all(self, matched_trips: tuple[MatchedTrip, ...]) -> None:
        """Saves a batch of trips"""
        rows = [self.convert_to_row(trip) for trip in matched_trips]
        cursor = self.connection.cursor()
        try:
            cursor.executemany(self.INSERT_SQL, rows)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def convert_to_row(self, trip: MatchedTrip) -> tuple:
        road_points = list(trip.road_points) if trip.status == "matched" else None
        return (
            trip.trip_id.dataset,
            trip.trip_id.taxi_id,
            trip.trip_id.trajectory_id,
            trip.algorithm,
            trip.status,
            Jsonb(road_points) if road_points is not None else None,
            Jsonb(trip.params),
        )

    def test_repo(self) -> str:
        count = self.fetch("SELECT count(*) FROM map_matching.matched_trajectories")[0][0]

        cursor = self.connection.cursor()
        try:
            cursor.execute(
                self.INSERT_SQL,
                ("repotest", "0", "0", "fmm", "failed", None, Jsonb({})),
            )
        finally:
            cursor.close()
            self.connection.rollback()
        return f"Matched Trip Repository has {count} rows, and a test insert succeeded (rolled back)"