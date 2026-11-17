from enum import Enum
from typing import Annotated

import typer

from mapmatching.repositories.config import Settings
from mapmatching.repositories.connection import connect
from mapmatching.repositories.trip_repository import TripRepository

#from mapmatching.algorithms.matcher import Matcher
#from mapmatching.algorithms.fmm_matcher import FmmMatcher
#from mapmatching.algorithms.stmatch_matcher import StMatcher
#from mapmatching.repositories.matched_trip_repository import MatchedTripRepository

class Algorithm(str, Enum):
    fmm = "fmm"
    stmatch = "stmatch"

def match(
        algorithm: Annotated[Algorithm, typer.Option(help="Which algorithm to use.")] = Algorithm.fmm,
        limit: Annotated[int | None, typer.Option(help="Maximum number of trips to match. Default: all")] = None,
        batch_size: Annotated[int, typer.Option(help="Trips fetched per batch.")] = 500,
        k: Annotated[int, typer.Option(help="Number of candidate roads per GPS point.")] = 8,
        radius: Annotated[float, typer.Option(help= "Candidate search radius, in the network's units.")] = 0.003,
        gps_error: Annotated[float, typer.Option(help="Expected GPS error, in the network's units.")] = 0.0005,
        dry_run: Annotated[bool, typer.Option(help="Match but do not save results.")] = False,
) -> None:
    """This command map matches trips from the database with the chosen algorithm."""

    connection = connect(Settings.load_env_info())

    try:
        trips = TripRepository(connection)
        batch = trips.get_batch(batch_number = 0, batch_size= batch_size)
        typer.echo(f"algorithm={algorithm.value}, fetched {len(batch)} trips")
    finally:
        connection.close()