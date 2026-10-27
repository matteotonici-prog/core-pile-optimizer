import numpy as np
import plotly.graph_objects as go
from plotly.colors import qualitative
from pilegroup import PileGroup

def _closed(poly):
    return np.vstack([poly, poly[:1]])

def _bounds(case, limits):
    """Reaction limits implied by each check type (my reading: confirm against evaluator.py)."""
    C, T = limits.compression_capacity, limits.tension_capacity
    if case.check_type == "No tension": return 0.0, C
    if case.check_type == "Tension":    return -T, None
    return -1e12, C                      # "Compression"

def make_figure(solution, load_case, limits):
    p = np.asarray(solution.coordinates)
    r = np.asarray(solution.reactions_by_case[load_case.name])
    g = PileGroup(p)
    ex, ey = g.resultant(load_case.n, load_case.mx, load_case.my)
    fig = go.Figure()
    fig.add_shape(type="rect", x0=-limits.max_width/2, x1=limits.max_width/2,
                  y0=-limits.max_depth/2, y1=limits.max_depth/2,
                  line=dict(dash="dash", color="#64748b"))

    # Classic no-tension kern (independent of load)
    k = g.kern() + g.centroid
    if len(k):
        k = _closed(k)
        fig.add_trace(go.Scatter(x=k[:,0], y=k[:,1], mode="lines", name="Kern (no tension)",
                      fill="toself", line=dict(color="#2563eb"), fillcolor="rgba(37,99,235,0.15)"))

    # Where the resultant of THIS combination may sit, given pile capacities
    if load_case.n > 1e-9:
        lo, hi = _bounds(load_case, limits)
        dom = g.reaction_domain(load_case.n, lo, hi)
        if len(dom):
            dom = _closed(dom / load_case.n + g.centroid)
            fig.add_trace(go.Scatter(x=dom[:,0], y=dom[:,1], mode="lines",
                          name="Capacity domain (this combination)",
                          line=dict(color="#7c3aed", dash="dash")))

    fig.add_trace(go.Scatter(x=p[:,0], y=p[:,1], mode="markers+text",
        text=[f"P{i+1}<br>{v:.0f}" for i, v in enumerate(r)], textposition="top center",
        marker=dict(size=18, color=r, colorscale="RdYlGn_r", colorbar=dict(title="kN")), name="Piles"))
    fig.add_trace(go.Scatter(x=[g.centroid[0]], y=[g.centroid[1]], mode="markers",
        marker=dict(symbol="x", size=15), name="Centroid"))
    if np.isfinite(ex):
        fig.add_trace(go.Scatter(x=[g.centroid[0]+ex], y=[g.centroid[1]+ey], mode="markers",
            marker=dict(symbol="star", size=17), name="Resultant"))
    fig.update_layout(height=650, title=load_case.name, xaxis_title="X (m)", yaxis_title="Y (m)")
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig

def make_moment_figure(solution, cases, limits):
    """All combinations on one plot in moment space: each combination's allowable (My, Mx)
    polygon at its own N, with the applied moment as a star. Works for low-N combinations
    where the eccentricity M/N blows up."""
    g = PileGroup(np.asarray(solution.coordinates))
    fig = go.Figure()
    for i, c in enumerate(cases):
        col = qualitative.Plotly[i % 10]
        if c.n > 1e-9:
            lo, hi = _bounds(c, limits)
            dom = g.reaction_domain(c.n, lo, hi)
            if len(dom):
                dom = _closed(dom)
                fig.add_trace(go.Scatter(x=dom[:,0], y=dom[:,1], mode="lines", name=c.name,
                                         legendgroup=c.name, line=dict(color=col)))
        fig.add_trace(go.Scatter(x=[c.my], y=[c.mx], mode="markers", legendgroup=c.name,
                                 showlegend=False, marker=dict(symbol="star", size=14, color=col)))
    fig.update_layout(height=600, title="Moment capacity by combination",
                      xaxis_title="My (kNm)", yaxis_title="Mx (kNm)")
    return fig
