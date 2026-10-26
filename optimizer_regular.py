from evaluator import evaluate
from layouts import regular_grid, perimeter_grid

def optimise_regular(load_cases, limits, min_piles, max_piles, max_results=10, spacing_steps=4, include_perimeter=True):
    found=[]
    nxmax=int(limits.max_width//limits.min_spacing)+1
    nymax=int(limits.max_depth//limits.min_spacing)+1
    for nx in range(2,nxmax+1):
        for ny in range(2,nymax+1):
            sx_values=[limits.min_spacing] if nx==1 else [limits.min_spacing+i*(limits.max_width/(nx-1)-limits.min_spacing)/max(spacing_steps-1,1) for i in range(spacing_steps)]
            sy_values=[limits.min_spacing] if ny==1 else [limits.min_spacing+i*(limits.max_depth/(ny-1)-limits.min_spacing)/max(spacing_steps-1,1) for i in range(spacing_steps)]
            for sx in sx_values:
                for sy in sy_values:
                    candidates=[("Regular full grid",regular_grid(nx,ny,sx,sy))]
                    if include_perimeter and nx>=3 and ny>=3: candidates.append(("Regular perimeter grid",perimeter_grid(nx,ny,sx,sy)))
                    for name,p in candidates:
                        if min_piles<=len(p)<=max_piles:
                            s=evaluate(p,load_cases,limits,name)
                            if s: found.append(s)
    found.sort(key=lambda s:s.score)
    return found[:max_results]
