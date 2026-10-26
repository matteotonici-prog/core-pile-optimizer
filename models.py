from dataclasses import dataclass

@dataclass(frozen=True)
class LoadCase:
    name: str
    n: float
    mx: float
    my: float
    check_type: str  # "Compression", "Tension", or "No tension"

@dataclass(frozen=True)
class DesignLimits:
    compression_capacity: float
    tension_capacity: float
    min_spacing: float
    max_width: float
    max_depth: float

@dataclass
class Solution:
    mode: str
    coordinates: list
    score: float
    number_of_piles: int
    footprint_width: float
    footprint_depth: float
    footprint_area: float
    max_compression: float
    max_tension: float
    compression_utilisation: float
    tension_utilisation: float
    gravity_reserve: float
    minimum_spacing: float
    governing_compression_case: str
    governing_tension_case: str
    reactions_by_case: dict
