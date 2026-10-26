import time
import numpy as np
from evaluator import evaluate
from layouts import random_layout
from pilegroup import minimum_distance

def optimise_free(load_cases, limits, min_piles, max_piles, max_results=5, population_size=30, generations=35, patience=10, mutation_scale=.30, regularity_preference=.2, random_seed=42, progress_callback=None):
    """Fast genetic search. Stops after max_results feasible pile counts have been found."""
    rng=np.random.default_rng(random_seed); results=[]
    counts=list(range(min_piles,max_piles+1)); total=max(1,len(counts)*generations); tick=0
    for n in counts:
        population=[]
        for _ in range(population_size*15):
            if len(population)>=population_size: break
            p=random_layout(n,limits,rng)
            if p is not None: population.append(p)
        if not population: continue
        best_score=float('inf'); stale=0; best_feasible=None
        for generation in range(generations):
            ranked=[]
            # Keep infeasible geometry out through repair; evaluator returns feasible only.
            for p in population:
                s=evaluate(p,load_cases,limits,"Free pile locations",regularity_preference)
                if s: ranked.append((s.score,p,s))
            ranked.sort(key=lambda z:z[0])
            if ranked:
                if ranked[0][0] < best_score-1e-5:
                    best_score=ranked[0][0]; best_feasible=ranked[0][2]; stale=0
                else: stale+=1
                elites=[z[1] for z in ranked[:max(3,min(len(ranked),population_size//4))]]
            else:
                # No feasible member yet: continue evolving all geometrically valid seeds.
                elites=population[:max(3,population_size//4)]; stale=0
            population=list(elites)
            while len(population)<population_size:
                parent=elites[rng.integers(len(elites))]
                child=_mutate(parent,limits,mutation_scale,rng)
                child=_repair(child,limits,rng)
                population.append(child)
            tick+=1
            if progress_callback: progress_callback(min(tick/total,1.0))
            if best_feasible and stale>=patience: break
        if best_feasible:
            results.append(best_feasible)
            results.sort(key=lambda s:s.score)
            if len(results)>=max_results: break
    return results[:max_results]

def _mutate(parent,limits,scale,rng):
    p=parent.copy(); count=max(1,int(np.ceil(len(p)*rng.uniform(.1,.3))))
    idx=rng.choice(len(p),count,replace=False)
    p[idx]+=rng.normal(0,scale*limits.min_spacing,(count,2))
    p[:,0]=np.clip(p[:,0],-limits.max_width/2,limits.max_width/2)
    p[:,1]=np.clip(p[:,1],-limits.max_depth/2,limits.max_depth/2)
    return p

def _repair(p,limits,rng,iterations=30):
    p=p.copy()
    for _ in range(iterations):
        changed=False
        for i in range(len(p)):
            for j in range(i+1,len(p)):
                v=p[j]-p[i]; d=np.linalg.norm(v)
                if d<limits.min_spacing:
                    u=v/d if d>1e-9 else rng.normal(size=2)/np.linalg.norm(rng.normal(size=2))
                    shift=.5*(limits.min_spacing-d+1e-4)*u; p[i]-=shift; p[j]+=shift; changed=True
        p[:,0]=np.clip(p[:,0],-limits.max_width/2,limits.max_width/2)
        p[:,1]=np.clip(p[:,1],-limits.max_depth/2,limits.max_depth/2)
        if not changed: break
    return p
