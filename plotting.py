import numpy as np
import plotly.graph_objects as go

from pilegroup import PileGroup


def make_figure(solution, load_case, limits, show_kern=True):
    points = np.asarray(solution.coordinates, dtype=float)
    reactions = np.asarray(solution.reactions_by_case[load_case.name], dtype=float)
    group = PileGroup(points)
    ex, ey = group.resultant(load_case.n, load_case.mx, load_case.my)

    figure = go.Figure()

    figure.add_shape(
        type="rect",
        x0=-limits.max_width / 2,
        x1=limits.max_width / 2,
        y0=-limits.max_depth / 2,
        y1=limits.max_depth / 2,
        line=dict(dash="dash", color="#64748b"),
        fillcolor="rgba(148,163,184,0.04)",
        layer="below",
    )

    if show_kern:
        kern = group.kern_polygon()
        if len(kern) >= 3:
            # kern_polygon is relative to the pile centroid. Move it into the
            # same global coordinate system as the pile layout.
            kern_global = kern + group.centroid
            kern_closed = np.vstack([kern_global, kern_global[0]])
            figure.add_trace(
                go.Scatter(
                    x=kern_closed[:, 0],
                    y=kern_closed[:, 1],
                    mode="lines",
                    fill="toself",
                    fillcolor="rgba(37,99,235,0.16)",
                    line=dict(color="#2563eb", width=2),
                    name="Pile-group kern",
                    hovertemplate="Kern boundary<extra></extra>",
                )
            )

    figure.add_trace(
        go.Scatter(
            x=points[:, 0],
            y=points[:, 1],
            mode="markers+text",
            text=[f"P{i + 1}<br>{value:.0f}" for i, value in enumerate(reactions)],
            textposition="top center",
            marker=dict(
                size=18,
                color=reactions,
                colorscale="RdYlGn_r",
                colorbar=dict(title="Reaction kN"),
                line=dict(color="#0f172a", width=1),
            ),
            name="Piles",
            hovertemplate=(
                "X=%{x:.2f} m<br>Y=%{y:.2f} m<br>"
                "Pile reaction=%{marker.color:.1f} kN<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[group.centroid[0]],
            y=[group.centroid[1]],
            mode="markers",
            marker=dict(symbol="x", size=15, color="#111827"),
            name="Pile-group centroid",
        )
    )

    if np.isfinite(ex) and np.isfinite(ey):
        resultant_x = group.centroid[0] + ex
        resultant_y = group.centroid[1] + ey
        figure.add_trace(
            go.Scatter(
                x=[resultant_x],
                y=[resultant_y],
                mode="markers",
                marker=dict(symbol="star", size=18, color="#7c3aed"),
                name="Load resultant",
                hovertemplate=(
                    f"Resultant<br>ex={ex:.3f} m<br>ey={ey:.3f} m"
                    "<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        height=650,
        title=f"{load_case.name}: pile reactions and no-tension kern",
        xaxis_title="X (m)",
        yaxis_title="Y (m)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=90, b=20),
    )
    figure.update_yaxes(scaleanchor="x", scaleratio=1)
    return figure
