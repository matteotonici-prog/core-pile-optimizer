from __future__ import annotations

from evaluator import evaluate_layout
from layouts import centred_perimeter_grid, centred_regular_grid
from models import DesignLimits, LoadCase, Solution


def optimise_regular(
    load_cases: list[LoadCase],
    limits: DesignLimits,
    min_piles: int,
    max_piles: int,
    spacing_steps: int = 5,
    include_perimeter: bool = True,
) -> list[Solution]:
    solutions: list[Solution] = []
    max_nx = int(limits.max_width // limits.min_spacing) + 1
    max_ny = int(limits.max_depth // limits.min_spacing) + 1

    for nx in range(2, max_nx + 1):
        for ny in range(2, max_ny + 1):
            for ix in range(spacing_steps):
                sx = limits.min_spacing + ix * max(0.0, limits.max_width / max(nx - 1, 1) - limits.min_spacing) / max(spacing_steps - 1, 1)
                for iy in range(spacing_steps):
                    sy = limits.min_spacing + iy * max(0.0, limits.max_depth / max(ny - 1, 1) - limits.min_spacing) / max(spacing_steps - 1, 1)

                    candidates = [("Regular full grid", centred_regular_grid(nx, ny, sx, sy))]
                    if include_perimeter and nx >= 3 and ny >= 3:
                        candidates.append(("Regular perimeter grid", centred_perimeter_grid(nx, ny, sx, sy)))

                    for name, coordinates in candidates:
                        if not min_piles <= len(coordinates) <= max_piles:
                            continue
                        result = evaluate_layout(coordinates, load_cases, limits, name, regularity_weight=0.0)
                        if result.feasible:
                            solutions.append(result)

    return _deduplicate(sorted(solutions, key=lambda result: result.score))


def _deduplicate(solutions: list[Solution], keep: int = 100) -> list[Solution]:
    unique: list[Solution] = []
    keys = set()
    for solution in solutions:
        rounded = tuple(sorted((round(x, 3), round(y, 3)) for x, y in solution.coordinates))
        if rounded not in keys:
            keys.add(rounded)
            unique.append(solution)
        if len(unique) >= keep:
            break
    return unique
