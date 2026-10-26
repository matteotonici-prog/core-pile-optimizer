import numpy as np


class PileGroup:

    def __init__(self, piles):

        self.piles = np.array(piles, dtype=float)

        self.x = self.piles[:, 0]
        self.y = self.piles[:, 1]

        self.n = len(self.piles)

        self.xc = np.mean(self.x)
        self.yc = np.mean(self.y)

        self.xr = self.x - self.xc
        self.yr = self.y - self.yc

        self.Ix = np.sum(self.yr ** 2)
        self.Iy = np.sum(self.xr ** 2)

    def reactions(self, N, Mx, My):

        reactions = np.full(self.n, N / self.n)

        if self.Ix > 0:
            reactions += Mx * self.yr / self.Ix

        if self.Iy > 0:
            reactions += My * self.xr / self.Iy

        return reactions

    def eccentricity(self, N, Mx, My):

        if abs(N) < 1e-6:
            return 999, 999

        ex = My / N
        ey = Mx / N

        return ex, ey

    def kern_check(self, N, Mx, My):

        ex, ey = self.eccentricity(N, Mx, My)

        width = max(self.x) - min(self.x)
        depth = max(self.y) - min(self.y)

        kx = width / 6
        ky = depth / 6

        inside = abs(ex) <= kx and abs(ey) <= ky

        margin_x = 1 - abs(ex) / max(kx, 1e-6)
        margin_y = 1 - abs(ey) / max(ky, 1e-6)

        return inside, min(margin_x, margin_y)
