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
        self.matrix = np.array([[np.sum(x*x), np.sum(x*y)], [np.sum(x*y), np.sum(y*y)]])
        if np.linalg.det(self.matrix) <= 1e-9:
            raise ValueError("Pile group is singular or nearly collinear.")

    def reactions(self, n, mx, my):
        x, y = self.relative[:, 0], self.relative[:, 1]
        a, b = np.linalg.solve(self.matrix, np.array([my, mx], dtype=float))
        return n / len(x) + a*x + b*y

    def resultant(self, n, mx, my):
        return (my/n, mx/n) if abs(n) > 1e-9 else (float("nan"), float("nan"))

def minimum_distance(coordinates):
    p = np.asarray(coordinates, dtype=float)
    d = np.sqrt(np.sum((p[:, None, :] - p[None, :, :])**2, axis=2))
    d[np.eye(len(p), dtype=bool)] = np.inf
    return float(np.min(d))

def footprint(coordinates):
    p = np.asarray(coordinates, dtype=float)
    w, d = float(np.ptp(p[:, 0])), float(np.ptp(p[:, 1]))
    return w, d, w*d
