from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class TripId:
   dataset: str
   taxi_id: str
   trajectory_id: str