from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from models import LoadCase, Solution
from pilegroup import PileGroup


def layout_figure(solution: Solution, load_case: LoadCase, max_width: float, max_depth: float):
    points = np.asarray(solution.coordinates, dtype=float)
    reactions = np.asarray(solution.reactions_by_case[load_case.name], dtype=float)
    group = PileGroup(points)
    rx, ry = group.resultant(load_case.n, load_case.mx, load_case.my)

    labels = [f"P{i + 1}<br>{reaction:.0f} kN" for i, reaction in enumerate(reactions)]
    utilisation_colour = reactions

    figure = go.Figure()
    figure.add_shape(
        type="rect",
        x0=-max_width / 2.0,
        x1=max_width / 2.0,
        y0=-max_depth / 2.0,
        y1=max_depth / 2.0,
        line=dict(color="#64748b", dash="dash"),
        fillcolor="rgba(148,163,184,0.06)",
        layer="below",
    )
    figure.add_trace(
        go.Scatter(
            x=points[:, 0],
            y=points[:, 1],
            mode="markers+text",
            text=labels,
            textposition="top center",
            marker=dict(
                size=18,
                color=utilisation_colour,
                colorscale="RdYlGn_r",
                colorbar=dict(title="Reaction kN"),
                line=dict(width=1, color="#0f172a"),
            ),
            name="Piles",
            hovertemplate="x=%{x:.2f} m<br>y=%{y:.2f} m<br>%{text}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[group.centroid[0]],
            y=[group.centroid[1]],
            mode="markers",
            marker=dict(symbol="x", size=15, color="#2563eb"),
            name="Pile-group centroid",
        )
    )
    if np.isfinite(rx) and np.isfinite(ry):
        figure.add_trace(
            go.Scatter(
                x=[group.centroid[0] + rx],
                y=[group.centroid[1] + ry],
                mode="markers",
                marker=dict(symbol="star", size=17, color="#7c3aed"),
                name="Load resultant",
            )
        )

    figure.update_layout(
        title=f"{solution.mode}: {load_case.name}",
        xaxis_title="X coordinate (m)",
        yaxis_title="Y coordinate (m)",
        height=650,
        legend=dict(orientation="h"),
        margin=dict(l=20, r=20, t=70, b=20),
    )
    figure.update_yaxes(scaleanchor="x", scaleratio=1)
    return figure
