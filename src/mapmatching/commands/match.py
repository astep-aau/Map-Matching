from enum import Enum
from typing import Annotated

import typer

from mapmatching.repositories.config import Settings
from mapmatching.repositories.connection import connect
from mapmatching.repositories.trip_repository import TripRepository

from mapmatching.algorithms.base_matcher import BaseMatcher
#from mapmatching.algorithms.fmm_matcher import FmmMatcher
#from mapmatching.algorithms.stmatch_matcher import StMatcher
from mapmatching.repositories.matched_trip_repository import MatchedTripRepository
from mapmatching.algorithms.network import load_network

class Algorithm(str, Enum):
    fmm = "fmm"
    stmatch = "stmatch"

def match(
        algorithm: Annotated[Algorithm, typer.Option(help="Which algorithm to use.")] = Algorithm.fmm,
        Batches: Annotated[int | None, typer.Option(help="Amount of batches to match. Default: all")] = None,
        batch_size: Annotated[int, typer.Option(help="Trips fetched per batch.")] = 500,
        k: Annotated[int, typer.Option(help="Number of candidate roads per GPS point.")] = 8,
        radius: Annotated[float, typer.Option(help= "Candidate search radius, in the network's units.")] = 300.0,
        gps_error: Annotated[float, typer.Option(help="Expected GPS error, in the network's units.")] = 50.0,
        dry_run: Annotated[bool, typer.Option(help="Match but do not save results.")] = False,
) -> None:
    """This command executes map matching to trips from the database with the chosen algorithm."""
    #this functionality should be exported to its own command potentially
    
    #create database connection
    settings = Settings.load_env_info()
    connection = connect(settings)
    #create network graph
    network, graph = load_network(settings)

    #instantiate either fmm matcher or stmatcher, with all their parameters, depending on which algorithm user selected
    if algorithm == Algorithm.stmatch:
        params = {"k": k, "radius": radius, "gps_error": gps_error} #later include: "vmax": vmax, "factor": factor
        #matcher = StMatcher(network, graph, params)
    else:
        params = {"k": k, "radius": radius, "gps_error": gps_error} #later include: "delta": delta
        #matcher = FmmMatcher(network, graph, params)

    #try fetching trajectories
    try:
        tripFetcher = TripRepository(connection)
        matchedtripUploader = MatchedTripRepository(connection)
        batch_number = 0

        while True:
            batch = tripFetcher.get_batch(batch_number = batch_number, batch_size= batch_size)
            if not batch or batch_number == Batches:
                break
            #results = [matcher.match_trip(trip) for trip in batch]
            #matchedtripUploader.save_all(results)
        
        typer.echo(f"algorithm={algorithm.value}, fetched {len(batch)} trips")
    finally:
        connection.close()