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

def _clip(poly, a, b):
    """Keep the part of a convex polygon where a·x <= b (Sutherland–Hodgman)."""
    out = []
    for P, Q in zip(poly, np.roll(poly, -1, axis=0)):
        fp, fq = a @ P - b, a @ Q - b
        if fp <= 0: out.append(P)
        if fp * fq < 0: out.append(P + (Q - P) * fp / (fp - fq))
    return np.array(out)

    # inside class PileGroup
    def reaction_domain(self, n=1.0, r_min=0.0, r_max=None, bound=1e9):
        """Polygon of (my, mx) about the centroid for which every pile reaction
        stays within [r_min, r_max] at axial load n. Empty array if infeasible.
        Divide by n (n>0) to get the resultant eccentricity (ex, ey)."""
        A = self.relative @ np.linalg.inv(self.matrix)       # row i = (M⁻¹ q_i)ᵀ
        poly = np.array([[-bound,-bound],[bound,-bound],[bound,bound],[-bound,bound]])
        base = n / len(self.relative)
        for a in A:
            poly = _clip(poly, -a, base - r_min)                          # R_i >= r_min
            if r_max is not None and len(poly): poly = _clip(poly, a, r_max - base)  # R_i <= r_max
            if len(poly) == 0: break
        return poly

    def kern(self):
        """No-tension kern as eccentricity (ex, ey) from the centroid."""
        return self.reaction_domain(1.0, 0.0, None)
