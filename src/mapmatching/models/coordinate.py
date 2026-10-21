from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Coordinate:
    lon: float
    lat: float