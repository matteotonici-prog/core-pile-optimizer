from __future__ import annotations

import numpy as np

from models import DesignLimits, LoadCase, Solution
from pilegroup import (
    PileGroup,
    footprint_dimensions,
    pairwise_minimum_distance,
    regularity_index,
)


def evaluate_layout(
    coordinates,
    load_cases: list[LoadCase],
    limits: DesignLimits,
    mode: str,
    regularity_weight: float = 0.0,
) -> Solution:
    points = np.asarray(coordinates, dtype=float)
    messages: list[str] = []
    reactions_by_case: dict[str, list[float]] = {}

    if len(points) < 3:
        return _failed_solution(points, mode, "At least three piles are required.")

    width, depth, area = footprint_dimensions(points)
    spacing = pairwise_minimum_distance(points)
    envelope_ok = width <= limits.max_width + 1e-9 and depth <= limits.max_depth + 1e-9
    spacing_ok = spacing >= limits.min_spacing - 1e-9

    penalty = 0.0
    if not envelope_ok:
        penalty += 1.0e6 * (
            max(0.0, width / limits.max_width - 1.0)
            + max(0.0, depth / limits.max_depth - 1.0)
        )
        messages.append("Pile layout exceeds the maximum footprint.")
    if not spacing_ok:
        penalty += 1.0e6 * (limits.min_spacing - spacing) / limits.min_spacing
        messages.append("Minimum centre-to-centre pile spacing is not satisfied.")

    try:
        group = PileGroup(points)
    except ValueError as exc:
        return _failed_solution(points, mode, str(exc), penalty + 1.0e9)

    max_comp = -np.inf
    min_reaction = np.inf
    comp_case = ""
    tension_case = ""
    gravity_reserve = np.inf
    comp_util = 0.0
    tension_util = 0.0

    for load_case in load_cases:
        reactions = group.reactions(load_case.n, load_case.mx, load_case.my)
        reactions_by_case[load_case.name] = reactions.tolist()

        case_max = float(np.max(reactions))
        case_min = float(np.min(reactions))

        if case_max > max_comp:
            max_comp = case_max
            comp_case = load_case.name
        if case_min < min_reaction:
            min_reaction = case_min
            tension_case = load_case.name

        case_comp_util = max(0.0, case_max) / limits.compression_capacity
        comp_util = max(comp_util, case_comp_util)
        if case_comp_util > 1.0:
            penalty += 1.0e6 * (case_comp_util - 1.0)

        if load_case.is_gravity:
            mean_reaction = load_case.n / len(points)
            reserve = case_min / mean_reaction if mean_reaction > 1e-9 else -np.inf
            gravity_reserve = min(gravity_reserve, reserve)
            if case_min < -1e-9:
                penalty += 2.0e6 * abs(case_min) / limits.compression_capacity
                messages.append(f"Gravity case '{load_case.name}' produces pile tension.")
        elif case_min < 0.0:
            if limits.tension_capacity <= 1e-9:
                case_tension_util = np.inf
                penalty += 2.0e6 * abs(case_min) / limits.compression_capacity
            else:
                case_tension_util = abs(case_min) / limits.tension_capacity
                tension_util = max(tension_util, case_tension_util)
                if case_tension_util > 1.0:
                    penalty += 2.0e6 * (case_tension_util - 1.0)

    if not np.isfinite(gravity_reserve):
        gravity_reserve = 0.0

    regularity = regularity_index(points)
    feasible = penalty < 1.0

    # Feasible layouts are ranked first. The remaining terms rank engineering efficiency.
    score = (
        penalty
        + 100.0 * comp_util
        + 120.0 * tension_util
        + 2.0 * len(points)
        + 0.10 * area
        + 15.0 * regularity_weight * regularity
        - 10.0 * max(-1.0, min(1.0, gravity_reserve))
    )

    if feasible:
        messages.append("All selected design constraints are satisfied.")

    return Solution(
        mode=mode,
        coordinates=points.tolist(),
        feasible=feasible,
        score=float(score),
        number_of_piles=len(points),
        footprint_width=width,
        footprint_depth=depth,
        footprint_area=area,
        max_compression=float(max_comp),
        max_tension=float(min(0.0, min_reaction)),
        max_compression_utilisation=float(comp_util),
        max_tension_utilisation=float(tension_util),
        gravity_reserve=float(gravity_reserve),
        minimum_spacing=spacing,
        regularity=regularity,
        governing_compression_case=comp_case,
        governing_tension_case=tension_case,
        reactions_by_case=reactions_by_case,
        messages=list(dict.fromkeys(messages)),
    )


def _failed_solution(points, mode, message, score=1.0e12) -> Solution:
    width, depth, area = (0.0, 0.0, 0.0)
    if len(points):
        width, depth, area = footprint_dimensions(points)
    return Solution(
        mode=mode,
        coordinates=np.asarray(points, dtype=float).tolist(),
        feasible=False,
        score=float(score),
        number_of_piles=len(points),
        footprint_width=width,
        footprint_depth=depth,
        footprint_area=area,
        max_compression=float("inf"),
        max_tension=float("-inf"),
        max_compression_utilisation=float("inf"),
        max_tension_utilisation=float("inf"),
        gravity_reserve=float("-inf"),
        minimum_spacing=pairwise_minimum_distance(points),
        regularity=1.0,
        governing_compression_case="",
        governing_tension_case="",
        reactions_by_case={},
        messages=[message],
    )
