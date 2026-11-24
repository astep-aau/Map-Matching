from enum import Enum
from typing import Annotated

import typer

from mapmatching.repositories.config import Settings
from mapmatching.repositories.connection import connect
from mapmatching.repositories.trip_repository import TripRepository

#from mapmatching.algorithms.fmm.fmm_matcher import FmmMatcher
#from mapmatching.algorithms.stmatch.stmatch_matcher import StMatcher
from mapmatching.repositories.matched_trip_repository import MatchedTripRepository
from mapmatching.algorithms.network import load_network

class Algorithm(str, Enum):
    fmm = "fmm"
    stmatch = "stmatch"

def match(
        algorithm: Annotated[Algorithm, typer.Option(help="Which algorithm to use.")] = Algorithm.fmm,
        dataset: Annotated[str, typer.Option(help="Dataset to match.")] = "traj_valid",
        limit: Annotated[int | None, typer.Option(help="Maximum number of trips to match. Default: all")] = None,
        batch_size: Annotated[int, typer.Option(help="Trips fetched per batch.")] = 500,
        k: Annotated[int, typer.Option(help="Number of candidate roads per GPS point.")] = 8,
        radius: Annotated[float, typer.Option(help= "Candidate search radius, in metres.")] = 300.0,
        gps_error: Annotated[float, typer.Option(help="Expected GPS error, in metres.")] = 50.0,
        dry_run: Annotated[bool, typer.Option(help="Match but do not save results.")] = False,
) -> None:
    """This command executes map matching to trips from the database with the chosen algorithm."""
    #this functionality should be exported to its own command potentially
    
    settings = Settings.load_env_info()
    #create network graph
    network, graph = load_network(settings)
    #create database connection
    connection = connect(settings)

    #instantiate either fmm matcher or stmatcher, with all their parameters, depending on which algorithm user selected
    if algorithm == Algorithm.stmatch:
        params = {"k": k, "radius": radius, "gps_error": gps_error} #later include: "vmax": vmax, "factor": factor
        #matcher = StMatcher(network, graph, params)
    else:
        params = {"k": k, "radius": radius, "gps_error": gps_error} #later include: "delta": delta
        #matcher = FmmMatcher(network, graph, params)

    #try fetching trajectories
    try:
        done = 0
        batch_number = 0

        tripFetcher = TripRepository(connection)
        matchedtripUploader = MatchedTripRepository(connection)

        while True:
            batch = tripFetcher.get_batch(dataset=dataset, batch_number = batch_number, batch_size= batch_size)
            if limit is not None:
                batch = batch[:limit - done]
            if not batch:
                break
            #results = [matcher.match_trip(trip) for trip in batch]
            #if not dry_run:
            #    matchedtripUploader.save_all(results)
            done += len(batch)
            batch_number += 1

            typer.echo(f"algorithm={algorithm.value}, fetched {len(batch)} trips")

    finally:
        connection.close()