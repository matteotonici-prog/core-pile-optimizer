import numpy as np

class PileGroup:
    def __init__(self,coordinates):
        p=np.asarray(coordinates,float)
        if p.ndim!=2 or p.shape[1]!=2 or len(p)<3: raise ValueError("At least three piles are required.")
        self.coordinates=p; self.centroid=p.mean(axis=0); self.relative=p-self.centroid
        x,y=self.relative[:,0],self.relative[:,1]
        self.matrix=np.array([[np.sum(x*x),np.sum(x*y)],[np.sum(x*y),np.sum(y*y)]],float)
        if np.linalg.det(self.matrix)<=1e-9: raise ValueError("Pile layout is singular or nearly collinear.")
    def reactions(self,n,mx,my):
        x,y=self.relative[:,0],self.relative[:,1]; a,b=np.linalg.solve(self.matrix,np.array([my,mx],float)); return n/len(x)+a*x+b*y
    def resultant(self,n,mx,my): return (my/n,mx/n) if abs(n)>1e-9 else (float('nan'),float('nan'))
    def kern_polygon(self):
        inv=np.linalg.inv(self.matrix); n=len(self.coordinates); poly=[np.array([-1e4,-1e4]),np.array([1e4,-1e4]),np.array([1e4,1e4]),np.array([-1e4,1e4])]
        for x,y in self.relative:
            a,b=np.array([x,y])@inv; poly=_clip(poly,a,b,1/n)
            if not poly:return np.empty((0,2))
        clean=[]
        for q in poly:
            if not clean or np.linalg.norm(q-clean[-1])>1e-8: clean.append(q)
        if len(clean)>1 and np.linalg.norm(clean[0]-clean[-1])<1e-8:clean.pop()
        return np.asarray(clean)
def _clip(poly,a,b,c):
    out=[]; prev=poly[-1]; vp=a*prev[0]+b*prev[1]+c; ip=vp>=-1e-10
    for cur in poly:
        vc=a*cur[0]+b*cur[1]+c; ic=vc>=-1e-10
        if ic!=ip:
            den=vp-vc
            if abs(den)>1e-12: out.append(prev+(vp/den)*(cur-prev))
        if ic:out.append(cur)
        prev,vp,ip=cur,vc,ic
    return out
def minimum_distance(p):
    p=np.asarray(p,float); d=np.sqrt(np.sum((p[:,None]-p[None,:])**2,axis=2)); d[np.eye(len(p),dtype=bool)]=np.inf; return float(d.min())
def footprint(p):
    p=np.asarray(p,float); w=float(np.ptp(p[:,0])); d=float(np.ptp(p[:,1])); return w,d,w*d
