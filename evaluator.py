import numpy as np
from models import Solution
from pilegroup import PileGroup, minimum_distance, footprint

def evaluate(coordinates, load_cases, limits, mode, regularity_weight=0.0):
    p = np.asarray(coordinates, dtype=float)
    try:
        group = PileGroup(p)
    except ValueError:
        return None
    width, depth, area = footprint(p)
    spacing = minimum_distance(p)
    penalty = 0.0
    if width > limits.max_width: penalty += 1e8*(width/limits.max_width-1)
    if depth > limits.max_depth: penalty += 1e8*(depth/limits.max_depth-1)
    if spacing < limits.min_spacing: penalty += 1e8*(limits.min_spacing-spacing)/limits.min_spacing

    reactions_by_case = {}
    max_comp, min_tension = 0.0, 0.0
    comp_util, tension_util = 0.0, 0.0
    comp_case, tension_case = "", ""
    gravity_reserve = 1e9

    for lc in load_cases:
        r = group.reactions(lc.n, lc.mx, lc.my)
        reactions_by_case[lc.name] = r.tolist()
        rmax, rmin = float(np.max(r)), float(np.min(r))
        if lc.check_type == "Compression":
            if rmax > max_comp: max_comp, comp_case = rmax, lc.name
            u = max(0.0, rmax)/limits.compression_capacity
            comp_util = max(comp_util, u)
            if u > 1: penalty += 1e7*(u-1)
        elif lc.check_type == "Tension":
            if rmin < min_tension: min_tension, tension_case = rmin, lc.name
            if rmin < 0:
                if limits.tension_capacity <= 1e-9:
                    tension_util = float("inf")
                    penalty += 1e7*abs(rmin)/limits.compression_capacity
                else:
                    u = abs(rmin)/limits.tension_capacity
                    tension_util = max(tension_util, u)
                    if u > 1: penalty += 1e7*(u-1)
        elif lc.check_type == "No tension":
            mean = lc.n/len(p)
            reserve = rmin/mean if mean > 1e-9 else -1e9
            gravity_reserve = min(gravity_reserve, reserve)
            if rmin < 0: penalty += 2e7*abs(rmin)/limits.compression_capacity

    if gravity_reserve == 1e9: gravity_reserve = 0.0
    # Soft alignment penalty for free mode: distance to rounded 0.25 m coordinates.
    irregularity = float(np.mean(np.abs(p/0.25 - np.round(p/0.25))))
    finite_tu = tension_util if np.isfinite(tension_util) else 1e6
    score = penalty + 100*comp_util + 120*finite_tu + 2*len(p) + 0.1*area + 10*regularity_weight*irregularity - 10*np.clip(gravity_reserve, -1, 1)
    feasible = penalty < 1.0
    if not feasible: return None
    return Solution(mode, p.tolist(), float(score), len(p), width, depth, area, max_comp, min_tension, comp_util, tension_util, gravity_reserve, spacing, comp_case, tension_case, reactions_by_case)
