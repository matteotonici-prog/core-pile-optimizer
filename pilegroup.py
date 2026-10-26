from __future__ import annotations

import numpy as np


TOL = 1.0e-9


class PileGroup:
    """Rigid pile-cap reaction model for equal axial pile stiffnesses.

    Sign convention:
    - Positive N produces pile compression.
    - Positive Mx increases compression at positive y.
    - Positive My increases compression at positive x.
    - Negative pile reaction means tension/uplift.
    """

    def __init__(self, coordinates):
        points = np.asarray(coordinates, dtype=float)
        if points.ndim != 2 or points.shape[1] != 2 or len(points) < 3:
            raise ValueError("At least three pile coordinates [x, y] are required.")
        if not np.isfinite(points).all():
            raise ValueError("Pile coordinates must be finite numbers.")

        self.coordinates = points
        self.n_piles = len(points)
        self.centroid = points.mean(axis=0)
        self.relative = points - self.centroid
        self.x = self.relative[:, 0]
        self.y = self.relative[:, 1]

        self.geometry_matrix = np.array(
            [
                [np.sum(self.x**2), np.sum(self.x * self.y)],
                [np.sum(self.x * self.y), np.sum(self.y**2)],
            ],
            dtype=float,
        )

        if np.linalg.det(self.geometry_matrix) <= TOL:
            raise ValueError("Pile layout is singular or nearly collinear.")

    def reactions(self, n_load: float, mx: float, my: float) -> np.ndarray:
        # Solve [sum(x^2), sum(xy); sum(xy), sum(y^2)] [a, b] = [My, Mx]
        a, b = np.linalg.solve(
            self.geometry_matrix,
            np.array([my, mx], dtype=float),
        )
        return n_load / self.n_piles + a * self.x + b * self.y

    def resultant(self, n_load: float, mx: float, my: float) -> tuple[float, float]:
        if abs(n_load) <= TOL:
            return float("nan"), float("nan")
        return my / n_load, mx / n_load


def pairwise_minimum_distance(coordinates) -> float:
    points = np.asarray(coordinates, dtype=float)
    if len(points) < 2:
        return float("inf")
    delta = points[:, None, :] - points[None, :, :]
    distance = np.sqrt(np.sum(delta**2, axis=2))
    distance[np.eye(len(points), dtype=bool)] = np.inf
    return float(np.min(distance))


def footprint_dimensions(coordinates) -> tuple[float, float, float]:
    points = np.asarray(coordinates, dtype=float)
    width = float(np.ptp(points[:, 0]))
    depth = float(np.ptp(points[:, 1]))
    return width, depth, width * depth


def regularity_index(coordinates, tolerance: float = 0.15) -> float:
    """Returns 0 for strongly aligned layouts and approaches 1 as scatter increases."""
    points = np.asarray(coordinates, dtype=float)
    if len(points) <= 2:
        return 0.0

    def clustered_count(values):
        ordered = np.sort(values)
        clusters = 1
        anchor = ordered[0]
        for value in ordered[1:]:
            if abs(value - anchor) > tolerance:
                clusters += 1
                anchor = value
        return clusters

    nx = clustered_count(points[:, 0])
    ny = clustered_count(points[:, 1])
    aligned_fraction = 1.0 - min(nx * ny, len(points)) / max(len(points), 1)
    # Higher alignment gives lower penalty.
    return float(np.clip(1.0 - aligned_fraction, 0.0, 1.0))
