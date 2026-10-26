import numpy as np
def grid(nx,ny,sx,sy):
 x=(np.arange(nx)-(nx-1)/2)*sx;y=(np.arange(ny)-(ny-1)/2)*sy;return np.array([(a,b) for b in y for a in x])
