import numpy as np
import plotly.graph_objects as go
from pilegroup import PileGroup

def make_figure(solution, load_case, limits):
    p=np.asarray(solution.coordinates); r=np.asarray(solution.reactions_by_case[load_case.name]); g=PileGroup(p); ex,ey=g.resultant(load_case.n,load_case.mx,load_case.my)
    fig=go.Figure()
    fig.add_shape(type="rect",x0=-limits.max_width/2,x1=limits.max_width/2,y0=-limits.max_depth/2,y1=limits.max_depth/2,line=dict(dash="dash",color="#64748b"))
    fig.add_trace(go.Scatter(x=p[:,0],y=p[:,1],mode="markers+text",text=[f"P{i+1}<br>{v:.0f}" for i,v in enumerate(r)],textposition="top center",marker=dict(size=18,color=r,colorscale="RdYlGn_r",colorbar=dict(title="kN")),name="Piles"))
    fig.add_trace(go.Scatter(x=[g.centroid[0]],y=[g.centroid[1]],mode="markers",marker=dict(symbol="x",size=15),name="Centroid"))
    if np.isfinite(ex): fig.add_trace(go.Scatter(x=[g.centroid[0]+ex],y=[g.centroid[1]+ey],mode="markers",marker=dict(symbol="star",size=17),name="Resultant"))
    fig.update_layout(height=650,title=load_case.name,xaxis_title="X (m)",yaxis_title="Y (m)"); fig.update_yaxes(scaleanchor="x",scaleratio=1)
    return fig
