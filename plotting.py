import numpy as np
import plotly.graph_objects as go
from pilegroup import PileGroup

def make_figure(solution,case,limits,core_x=0.,core_y=0.):
    p=np.asarray(solution.coordinates);r=np.asarray(solution.reactions_by_case[case.name]);g=PileGroup(p);ex,ey=g.resultant(case.n,case.mx,case.my);fig=go.Figure()
    fig.add_shape(type='rect',x0=-limits.max_width/2,x1=limits.max_width/2,y0=-limits.max_depth/2,y1=limits.max_depth/2,line=dict(dash='dash',color='#64748b'),fillcolor='rgba(148,163,184,.04)',layer='below')
    k=g.kern_polygon()+g.centroid
    if len(k)>=3:
        kc=np.vstack([k,k[0]]);fig.add_trace(go.Scatter(x=kc[:,0],y=kc[:,1],mode='lines',fill='toself',fillcolor='rgba(37,99,235,.16)',line=dict(color='#2563eb',width=2),name='Pile-group kern'))
    fig.add_trace(go.Scatter(x=p[:,0],y=p[:,1],mode='markers+text',text=[f'P{i+1}<br>{v:.0f}' for i,v in enumerate(r)],textposition='top center',marker=dict(size=18,color=r,colorscale='RdYlGn_r',colorbar=dict(title='Reaction kN'),line=dict(color='#0f172a',width=1)),name='Piles'))
    fig.add_trace(go.Scatter(x=[g.centroid[0]],y=[g.centroid[1]],mode='markers',marker=dict(symbol='x',size=15,color='#111827'),name='Pile centroid'))
    fig.add_trace(go.Scatter(x=[core_x],y=[core_y],mode='markers',marker=dict(symbol='diamond',size=15,color='#f97316'),name='Core centre'))
    if np.isfinite(ex):fig.add_trace(go.Scatter(x=[g.centroid[0]+ex],y=[g.centroid[1]+ey],mode='markers',marker=dict(symbol='star',size=18,color='#7c3aed'),name='Load resultant'))
    fig.update_layout(height=650,title=f'{case.name}: piles, kern, core centre and resultant',xaxis_title='X (m)',yaxis_title='Y (m)',legend=dict(orientation='h'));fig.update_yaxes(scaleanchor='x',scaleratio=1);return fig
