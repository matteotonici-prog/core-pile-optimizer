from __future__ import annotations

import numpy as np


def centred_regular_grid(nx: int, ny: int, sx: float, sy: float) -> np.ndarray:
    x = (np.arange(nx) - (nx - 1) / 2.0) * sx
    y = (np.arange(ny) - (ny - 1) / 2.0) * sy
    return np.array([(xi, yi) for yi in y for xi in x], dtype=float)


def centred_perimeter_grid(nx: int, ny: int, sx: float, sy: float) -> np.ndarray:
    grid = centred_regular_grid(nx, ny, sx, sy)
    xmax = np.max(np.abs(grid[:, 0]))
    ymax = np.max(np.abs(grid[:, 1]))
    mask = np.isclose(np.abs(grid[:, 0]), xmax) | np.isclose(np.abs(grid[:, 1]), ymax)
    return grid[mask]


def seed_free_layout(
    n_piles: int,
    max_width: float,
    max_depth: float,
    min_spacing: float,
    rng: np.random.Generator,
    attempts: int = 4000,
) -> np.ndarray | None:
    """Sequential random placement with some boundary bias for moment resistance."""
    points: list[np.ndarray] = []
    half_w = max_width / 2.0
    half_d = max_depth / 2.0

    for _ in range(attempts):
        if len(points) >= n_piles:
            break

        if rng.random() < 0.55:
            # Bias some seeds towards the outer bands, while retaining full freedom.
            side = rng.integers(4)
            if side == 0:
                candidate = np.array([rng.uniform(-half_w, half_w), rng.uniform(0.65 * half_d, half_d)])
            elif side == 1:
                candidate = np.array([rng.uniform(-half_w, half_w), rng.uniform(-half_d, -0.65 * half_d)])
            elif side == 2:
                candidate = np.array([rng.uniform(0.65 * half_w, half_w), rng.uniform(-half_d, half_d)])
            else:
                candidate = np.array([rng.uniform(-half_w, -0.65 * half_w), rng.uniform(-half_d, half_d)])
        else:
            candidate = np.array([rng.uniform(-half_w, half_w), rng.uniform(-half_d, half_d)])

        if all(np.linalg.norm(candidate - point) >= min_spacing for point in points):
            points.append(candidate)

    if len(points) != n_piles:
        return None
    return np.asarray(points, dtype=float)
