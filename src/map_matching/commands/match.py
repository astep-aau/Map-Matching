from enum import Enum
from typing import Annotated

import typer

from map_matching.repositories.config import Settings
from map_matching.repositories.connection import connect
from map_matching.repositories.trip_repository import TripRepository
from map_matching.repositories.road_segment_repository import RoadSegmentRepository

from map_matching.algorithms.fmm.fmm_matcher import FMMMatcher
from map_matching.algorithms.stmatch.st_matcher import STMatcher
from map_matching.repositories.matched_trip_repository import MatchedTripRepository
from map_matching.algorithms.network import load_network, load_ubodt

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
        delta: Annotated[float, typer.Option(help="Delta value given to Ubodt.")] = 3000.0,
        vmax: Annotated[float, typer.Option(help="Maximum speed of the vehicle, in metres per second.")] = 30.0,
        factor: Annotated[float, typer.Option(help="Factor for the STmatch algorithm.")] = 1.5,
        dry_run: Annotated[bool, typer.Option(help="Match but do not save results.")] = False,
) -> None:
    """This command executes map matching to trips from the database with the chosen algorithm."""
    #this functionality should be exported to its own command potentially
    
    settings = Settings.load_env_info()
    #create database connection
    connection = connect(settings)

    #try fetching trajectories
    try:
        done = 0
        batch_number = 0
        total_matched = 0
        total_failed = 0

        trip_fetcher = TripRepository(connection)
        road_segment_fetcher = RoadSegmentRepository(connection)
        matched_trip_uploader = MatchedTripRepository(connection)
        network, graph = load_network(road_segment_fetcher)

        #instantiate either fmm matcher or stmatcher, with all their parameters, depending on which algorithm user selected
        if algorithm == Algorithm.stmatch:
            params = {"k": k, "radius": radius, "gps_error": gps_error, "vmax": vmax, "factor": factor}
            matcher = STMatcher(network, graph, params)
        else: 
            params = {"k": k, "radius": radius, "gps_error": gps_error, "delta": delta} 
            ubodt = load_ubodt(network, graph, delta)
            matcher = FMMMatcher(network, graph, ubodt, params)

        while True:
            batch = trip_fetcher.get_batch(dataset=dataset, batch_number = batch_number, batch_size= batch_size)
            
            if limit is not None:
                batch = batch[:limit - done]
            
            if not batch:
                break
            results = [matcher.match_trip(trip) for trip in batch]
            
            if not dry_run:
                matched_trip_uploader.save_all(results)
            failed = sum(1 for r in results if r.status == "failed")
            total_failed += failed
            total_matched += len(results) - failed
            
            done += len(batch)
            batch_number += 1
   
        typer.echo(
            f"Done. algorithm={algorithm.value}, trips={done}, "
            f"matched={total_matched}, failed={total_failed}, dry_run={dry_run}"
        )

    finally:
        connection.close()