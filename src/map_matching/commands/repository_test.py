from map_matching.repositories.config import Settings
from map_matching.repositories.connection import connect
from map_matching.repositories.node_repository import NodeRepository
from map_matching.repositories.road_segment_repository import RoadSegmentRepository
from map_matching.repositories.trip_repository import TripRepository
from map_matching.repositories.matched_trip_repository import MatchedTripRepository

def repository_test() -> None:
    print("Testing repositories...")
    connection = connect(Settings.load_env_info())

    try:
        repositories = [
            NodeRepository(connection),
            TripRepository(connection),
            RoadSegmentRepository(connection),
            MatchedTripRepository(connection),
        ]
        for repository in repositories:
            name = type(repository).__name__
            try:
                print(name + ": " + repository.test_repository())
            except Exception as error:
                print(name + " Failed... error: " + str(error))
                connection.rollback()
    finally:
        connection.close()