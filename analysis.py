import numpy as np
from models import LoadCase,Solution
from pilegroup import PileGroup,minimum_distance,footprint

def create_cases(loads,combos,core_x=0.0,core_y=0.0,pile_centroid=(0.0,0.0)):
    comp={str(r['Load']):r for _,r in loads.iterrows()}; names=list(comp); cases=[]
    dx=core_x-pile_centroid[0]; dy=core_y-pile_centroid[1]
    for _,row in combos.iterrows():
        n=mx=my=0.0
        for name in names:
            f=float(row.get(name,0.0)); item=comp[name]; ni=f*float(item['N (kN)']); n+=ni; mx+=f*float(item['Mx (kNm)'])+ni*dy; my+=f*float(item['My (kNm)'])+ni*dx
        cases.append(LoadCase(str(row['Combination']),n,mx,my,str(row['Check'])))
    return cases

def evaluate(coords,cases,limits,mode,require_envelope=True):
    try:g=PileGroup(coords)
    except ValueError:return None
    w,d,a=footprint(coords); spacing=minimum_distance(coords); penalty=0.0
    if require_envelope and (w>limits.max_width or d>limits.max_depth): penalty+=1e8
    if spacing<limits.min_spacing: penalty+=1e8
    rb={}; mc=0.; mt=0.; cu=tu=0.; gr=1e9; cc=tc=''
    for lc in cases:
        r=g.reactions(lc.n,lc.mx,lc.my); rb[lc.name]=r.tolist(); rmax=float(r.max()); rmin=float(r.min())
        if lc.check_type=='Compression':
            if rmax>mc:mc,cc=rmax,lc.name
            u=max(0,rmax)/limits.compression_capacity; cu=max(cu,u); penalty+=max(0,u-1)*1e7
        elif lc.check_type=='Tension':
            if rmin<mt:mt,tc=rmin,lc.name
            if rmin<0:
                u=abs(rmin)/limits.tension_capacity if limits.tension_capacity>0 else 1e6; tu=max(tu,u); penalty+=max(0,u-1)*1e7
        elif lc.check_type=='No tension':
            reserve=rmin/(lc.n/len(coords)) if lc.n>0 else -1e9; gr=min(gr,reserve); penalty+=abs(min(0,rmin))/limits.compression_capacity*2e7
    if gr==1e9:gr=0
    if penalty>=1:return None
    score=100*cu+120*tu+2*len(coords)+.1*a-10*np.clip(gr,-1,1)
    return Solution(mode,np.asarray(coords).tolist(),float(score),len(coords),w,d,a,mc,mt,cu,tu,gr,spacing,cc,tc,rb)
