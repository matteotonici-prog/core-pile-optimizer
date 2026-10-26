import numpy as np


class PileGroup:
    """Rigid cap, equal axial pile stiffness. Positive reaction is compression."""

    def __init__(self, coordinates):
        p = np.asarray(coordinates, dtype=float)
        if p.ndim != 2 or p.shape[1] != 2 or len(p) < 3:
            raise ValueError("At least three [x, y] pile coordinates are required.")

        self.coordinates = p
        self.centroid = p.mean(axis=0)
        self.relative = p - self.centroid
        x, y = self.relative[:, 0], self.relative[:, 1]

        self.matrix = np.array(
            [
                [np.sum(x * x), np.sum(x * y)],
                [np.sum(x * y), np.sum(y * y)],
            ],
            dtype=float,
        )

        if np.linalg.det(self.matrix) <= 1e-9:
            raise ValueError("Pile group is singular or nearly collinear.")

    def reactions(self, n, mx, my):
        x, y = self.relative[:, 0], self.relative[:, 1]
        a, b = np.linalg.solve(self.matrix, np.array([my, mx], dtype=float))
        return n / len(x) + a * x + b * y

    def resultant(self, n, mx, my):
        return (my / n, mx / n) if abs(n) > 1e-9 else (float("nan"), float("nan"))

    def kern_polygon(self):
        """Return the exact no-tension kern polygon for this discrete pile group.

        Coordinates are relative to the pile-group centroid. A resultant located
        inside this polygon gives non-negative reactions in every equal-stiffness
        pile under a positive axial load.
        """
        inverse = np.linalg.inv(self.matrix)
        x = self.relative[:, 0]
        y = self.relative[:, 1]
        n_piles = len(self.coordinates)

        # For unit N at eccentricity [ex, ey]:
        # [a, b] = inv(matrix) @ [ex, ey]
        # reaction_i = 1/n + a*x_i + b*y_i >= 0
        half_planes = []
        for xi, yi in zip(x, y):
            row = np.array([xi, yi], dtype=float) @ inverse
            half_planes.append((float(row[0]), float(row[1]), 1.0 / n_piles))

        span = max(np.ptp(self.coordinates[:, 0]), np.ptp(self.coordinates[:, 1]), 1.0)
        bound = 10.0 * span
        polygon = [
            np.array([-bound, -bound]),
            np.array([bound, -bound]),
            np.array([bound, bound]),
            np.array([-bound, bound]),
        ]

        for coefficient_ex, coefficient_ey, constant in half_planes:
            polygon = _clip_polygon(
                polygon,
                coefficient_ex,
                coefficient_ey,
                constant,
            )
            if not polygon:
                return np.empty((0, 2), dtype=float)

        polygon = _remove_duplicate_vertices(polygon)
        return np.asarray(polygon, dtype=float)


def _remove_duplicate_vertices(polygon, tolerance=1e-9):
    cleaned = []
    for point in polygon:
        if not cleaned or np.linalg.norm(point - cleaned[-1]) > tolerance:
            cleaned.append(point)
    if len(cleaned) > 1 and np.linalg.norm(cleaned[0] - cleaned[-1]) <= tolerance:
        cleaned.pop()
    return cleaned


def _clip_polygon(polygon, a, b, c, tolerance=1e-10):
    """Clip a convex polygon by a*ex + b*ey + c >= 0."""
    if not polygon:
        return []

    clipped = []
    previous = polygon[-1]
    previous_value = a * previous[0] + b * previous[1] + c
    previous_inside = previous_value >= -tolerance

    for current in polygon:
        current_value = a * current[0] + b * current[1] + c
        current_inside = current_value >= -tolerance

        if current_inside != previous_inside:
            denominator = previous_value - current_value
            if abs(denominator) > tolerance:
                fraction = previous_value / denominator
                intersection = previous + fraction * (current - previous)
                clipped.append(intersection)

        if current_inside:
            clipped.append(current)

        previous = current
        previous_value = current_value
        previous_inside = current_inside

    return clipped


def minimum_distance(coordinates):
    p = np.asarray(coordinates, dtype=float)
    d = np.sqrt(np.sum((p[:, None, :] - p[None, :, :]) ** 2, axis=2))
    d[np.eye(len(p), dtype=bool)] = np.inf
    return float(np.min(d))


def footprint(coordinates):
    p = np.asarray(coordinates, dtype=float)
    width = float(np.ptp(p[:, 0]))
    depth = float(np.ptp(p[:, 1]))
    return width, depth, width * depth
