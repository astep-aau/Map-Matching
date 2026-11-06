from mapmatching.repositories.config import Settings
from mapmatching.repositories.connection import connect
from mapmatching.repositories.node_repository import NodeRepository
from mapmatching.repositories.road_segment_repository import RoadSegmentRepository
from mapmatching.repositories.trip_repository import TripRepository

def repotest() -> None:
    print("Testing repositories...")
    connection = connect(Settings.load_env_info())

    try:
        repositories = [
            NodeRepository(connection),
            TripRepository(connection),
            RoadSegmentRepository(connection)
        ]
        for repository in repositories:
            name = type(repository).__name__
            try:
                print(name + ": " + repository.test_repo())
            except Exception as error:
                print(name + " Failed... error: " + str(error))
                connection.rollback()
    finally:
        connection.close()