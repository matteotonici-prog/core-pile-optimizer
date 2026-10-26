import numpy as np

from pilegroup import PileGroup
from layouts import rectangular_layout
from layouts import perimeter_layout


def run_optimization(
    loadcases,
    compression_capacity,
    tension_capacity,
    max_width,
    max_depth,
    spacing
):

    solutions = []

    for nx in range(2, 11):

        for ny in range(2, 11):

            width = (nx - 1) * spacing
            depth = (ny - 1) * spacing

            if width > max_width:
                continue

            if depth > max_depth:
                continue

            layouts = [

                rectangular_layout(
                    nx,
                    ny,
                    spacing
                ),

                perimeter_layout(
                    nx,
                    ny,
                    spacing
                )
            ]

            for layout in layouts:

                pg = PileGroup(layout)

                gravity = loadcases[0]

                inside, kern_margin = pg.kern_check(
                    gravity["N"],
                    gravity["Mx"],
                    gravity["My"]
                )

                if not inside:
                    continue

                valid = True

                max_compression = 0
                max_tension = 0

                for lc in loadcases:

                    pile_loads = pg.reactions(
                        lc["N"],
                        lc["Mx"],
                        lc["My"]
                    )

                    compression = np.max(pile_loads)
                    tension = np.min(pile_loads)

                    max_compression = max(
                        max_compression,
                        compression
                    )

                    max_tension = min(
                        max_tension,
                        tension
                    )

                    if compression > compression_capacity:
                        valid = False

                    if (
                        tension < 0
                        and abs(tension)
                        > tension_capacity
                    ):
                        valid = False

                if not valid:
                    continue

                area = width * depth

                score = (

                    100
                    * (
                        max_compression
                        / compression_capacity
                    )

                    + 0.05 * area

                    + 0.5 * len(layout)

                    - 20 * kern_margin
                )

                solutions.append({

                    "layout": layout,
                    "n_piles": len(layout),
                    "score": score,
                    "area": area,
                    "max_compression": max_compression,
                    "max_tension": max_tension,
                    "kern_margin": kern_margin
                })

    solutions.sort(
        key=lambda x: x["score"]
    )

    return solutions
