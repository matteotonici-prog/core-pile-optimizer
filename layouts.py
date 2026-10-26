import numpy as np

def regular_grid(nx, ny, sx, sy):
    xs = (np.arange(nx)-(nx-1)/2)*sx
    ys = (np.arange(ny)-(ny-1)/2)*sy
    return np.array([(x,y) for y in ys for x in xs], dtype=float)

def perimeter_grid(nx, ny, sx, sy):
    p = regular_grid(nx, ny, sx, sy)
    return p[np.isclose(abs(p[:,0]), max(abs(p[:,0]))) | np.isclose(abs(p[:,1]), max(abs(p[:,1])))]

def random_layout(n, limits, rng, attempts=5000):
    points=[]
    for _ in range(attempts):
        if len(points)==n: return np.asarray(points)
        # 60% edge-biased candidates improve overturning resistance and convergence.
        if rng.random() < .6:
            side=rng.integers(4); hw=limits.max_width/2; hd=limits.max_depth/2
            if side==0: q=np.array([rng.uniform(-hw,hw), rng.uniform(.65*hd,hd)])
            elif side==1: q=np.array([rng.uniform(-hw,hw), rng.uniform(-hd,-.65*hd)])
            elif side==2: q=np.array([rng.uniform(.65*hw,hw), rng.uniform(-hd,hd)])
            else: q=np.array([rng.uniform(-hw,-.65*hw), rng.uniform(-hd,hd)])
        else:
            q=np.array([rng.uniform(-limits.max_width/2, limits.max_width/2), rng.uniform(-limits.max_depth/2, limits.max_depth/2)])
        if all(np.linalg.norm(q-a)>=limits.min_spacing for a in points): points.append(q)
    return None
