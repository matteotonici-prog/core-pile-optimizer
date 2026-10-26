from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from evaluator import evaluate_layout
from models import DesignLimits, LoadCase
from pilegroup import PileGroup


st.set_page_config(page_title="Bespoke Pile Layout", layout="wide")
st.title("Bespoke Pile Layout Check")
st.caption(
    "Check an engineer-defined pile arrangement using the same rigid-cap, "
    "equal-pile-stiffness calculation model as the optimiser."
)


def default_loads() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Load": "Dead", "N (kN)": 32000.0, "Mx (kNm)": 10000.0, "My (kNm)": 7000.0},
            {"Load": "Live", "N (kN)": 8000.0, "Mx (kNm)": 5000.0, "My (kNm)": 3000.0},
            {"Load": "Wx", "N (kN)": 0.0, "Mx (kNm)": 35000.0, "My (kNm)": 2000.0},
            {"Load": "Wy", "N (kN)": 0.0, "Mx (kNm)": 2000.0, "My (kNm)": 40000.0},
        ]
    )


def default_combinations() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Combination": "D + L", "Check": "No tension", "Dead": 1.0, "Live": 1.0, "Wx": 0.0, "Wy": 0.0},
            {"Combination": "D + L + Wx", "Check": "Compression", "Dead": 1.0, "Live": 1.0, "Wx": 1.0, "Wy": 0.0},
            {"Combination": "D + L + Wy", "Check": "Compression", "Dead": 1.0, "Live": 1.0, "Wx": 0.0, "Wy": 1.0},
            {"Combination": "0.9D + Wx", "Check": "Tension", "Dead": 0.9, "Live": 0.0, "Wx": 1.0, "Wy": 0.0},
            {"Combination": "0.9D + Wy", "Check": "Tension", "Dead": 0.9, "Live": 0.0, "Wx": 0.0, "Wy": 1.0},
        ]
    )


def default_piles() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Pile": "P1", "X (m)": -4.0, "Y (m)": -3.0},
            {"Pile": "P2", "X (m)": 0.0, "Y (m)": -3.0},
            {"Pile": "P3", "X (m)": 4.0, "Y (m)": -3.0},
            {"Pile": "P4", "X (m)": -4.0, "Y (m)": 3.0},
            {"Pile": "P5", "X (m)": 0.0, "Y (m)": 3.0},
            {"Pile": "P6", "X (m)": 4.0, "Y (m)": 3.0},
        ]
    )


if "bespoke_loads" not in st.session_state:
    # If the existing main page has already stored its tables, use them.
    st.session_state.bespoke_loads = st.session_state.get("loads_df", default_loads()).copy()
if "bespoke_combinations" not in st.session_state:
    st.session_state.bespoke_combinations = st.session_state.get("combos_df", default_combinations()).copy()
if "bespoke_piles" not in st.session_state:
    st.session_state.bespoke_piles = default_piles()


loads_tab, combinations_tab, piles_tab = st.tabs(
    ["Loads", "Combinations", "Pile coordinates"]
)

with loads_tab:
    st.write("Enter the load effects at the **core centre**.")
    loads = st.data_editor(
        st.session_state.bespoke_loads,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="bespoke_load_editor",
    )
    if st.button("＋ Add load component", key="bespoke_add_load"):
        new_row = pd.DataFrame(
            [{"Load": f"Load {len(loads) + 1}", "N (kN)": 0.0, "Mx (kNm)": 0.0, "My (kNm)": 0.0}]
        )
        st.session_state.bespoke_loads = pd.concat([loads, new_row], ignore_index=True)
        st.rerun()
    st.session_state.bespoke_loads = loads

with combinations_tab:
    load_names = [str(value) for value in loads["Load"].tolist()]
    combinations = st.session_state.bespoke_combinations.copy()
    for load_name in load_names:
        if load_name not in combinations.columns:
            combinations[load_name] = 0.0
    combinations = combinations[
        [column for column in ["Combination", "Check", *load_names] if column in combinations.columns]
    ]
    combinations = st.data_editor(
        combinations,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="bespoke_combination_editor",
        column_config={
            "Check": st.column_config.SelectboxColumn(
                options=["Compression", "Tension", "No tension"],
                required=True,
            )
        },
    )
    if st.button("＋ Add combination", key="bespoke_add_combination"):
        new_row = {
            "Combination": f"Combination {len(combinations) + 1}",
            "Check": "Compression",
            **{load_name: 0.0 for load_name in load_names},
        }
        st.session_state.bespoke_combinations = pd.concat(
            [combinations, pd.DataFrame([new_row])], ignore_index=True
        )
        st.rerun()
    st.session_state.bespoke_combinations = combinations

with piles_tab:
    st.write("Enter the bespoke pile names and global X-Y coordinates.")
    piles = st.data_editor(
        st.session_state.bespoke_piles,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="bespoke_pile_editor",
    )
    if st.button("＋ Add pile", key="bespoke_add_pile"):
        new_row = pd.DataFrame(
            [{"Pile": f"P{len(piles) + 1}", "X (m)": 0.0, "Y (m)": 0.0}]
        )
        st.session_state.bespoke_piles = pd.concat([piles, new_row], ignore_index=True)
        st.rerun()
    st.session_state.bespoke_piles = piles


left, middle, right = st.columns(3)
with left:
    st.subheader("Core centre")
    core_x = st.number_input("Core centre X (m)", value=0.0, step=0.1)
    core_y = st.number_input("Core centre Y (m)", value=0.0, step=0.1)
with middle:
    st.subheader("Pile limits")
    compression_capacity = st.number_input(
        "Compression capacity per pile (kN)", min_value=1.0, value=2500.0
    )
    tension_capacity = st.number_input(
        "Tension capacity per pile (kN)", min_value=0.0, value=300.0
    )
    pile_diameter = st.number_input("Pile diameter (m)", min_value=0.1, value=0.9)
    spacing_factor = st.number_input(
        "Minimum spacing / pile diameter", min_value=1.0, value=3.0
    )
with right:
    st.subheader("Plot limits")
    plot_width = st.number_input("Plot X extent (m)", min_value=1.0, value=16.0)
    plot_depth = st.number_input("Plot Y extent (m)", min_value=1.0, value=12.0)

st.info(
    "The entered load moments are taken about the core centre. The program transfers "
    "each load component to the pile-group centroid using the axial-load eccentricity."
)


def build_cases(load_table, combination_table, pile_centroid):
    component = {str(row["Load"]): row for _, row in load_table.iterrows()}
    dx = float(core_x - pile_centroid[0])
    dy = float(core_y - pile_centroid[1])
    cases = []

    for _, combination in combination_table.iterrows():
        axial = 0.0
        mx_at_pile_centroid = 0.0
        my_at_pile_centroid = 0.0

        for load_name, load in component.items():
            factor = float(combination.get(load_name, 0.0))
            factored_axial = factor * float(load["N (kN)"])
            axial += factored_axial
            mx_at_pile_centroid += (
                factor * float(load["Mx (kNm)"]) + factored_axial * dy
            )
            my_at_pile_centroid += (
                factor * float(load["My (kNm)"]) + factored_axial * dx
            )

        check_type = str(combination["Check"])
        cases.append(
            LoadCase(
                name=str(combination["Combination"]),
                n=axial,
                mx=mx_at_pile_centroid,
                my=my_at_pile_centroid,
                check_compression=check_type == "Compression",
                check_tension=check_type == "Tension",
                require_all_piles_in_compression=check_type == "No tension",
            )
        )
    return cases


def bespoke_figure(solution, load_case, limits, entered_piles):
    points = np.asarray(solution.coordinates, dtype=float)
    reactions = np.asarray(solution.reactions_by_case[load_case.name], dtype=float)
    group = PileGroup(points)
    ex, ey = group.resultant(load_case.n, load_case.mx, load_case.my)
    figure = go.Figure()

    figure.add_shape(
        type="rect",
        x0=-limits.max_width / 2.0,
        x1=limits.max_width / 2.0,
        y0=-limits.max_depth / 2.0,
        y1=limits.max_depth / 2.0,
        line=dict(color="#64748b", dash="dash"),
        fillcolor="rgba(148,163,184,0.04)",
        layer="below",
    )

    # Kern is mandatory on the bespoke page.
    kern = group.kern_polygon()
    if len(kern) >= 3:
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
            )
        )

    pile_names = entered_piles["Pile"].astype(str).tolist()
    figure.add_trace(
        go.Scatter(
            x=points[:, 0],
            y=points[:, 1],
            mode="markers+text",
            text=[f"{name}<br>{value:.0f} kN" for name, value in zip(pile_names, reactions)],
            textposition="top center",
            marker=dict(
                size=18,
                color=reactions,
                colorscale="RdYlGn_r",
                colorbar=dict(title="Reaction kN"),
                line=dict(width=1, color="#0f172a"),
            ),
            name="Piles",
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
    figure.add_trace(
        go.Scatter(
            x=[core_x],
            y=[core_y],
            mode="markers",
            marker=dict(symbol="diamond", size=16, color="#f97316"),
            name="Core centre",
        )
    )
    if np.isfinite(ex) and np.isfinite(ey):
        figure.add_trace(
            go.Scatter(
                x=[group.centroid[0] + ex],
                y=[group.centroid[1] + ey],
                mode="markers",
                marker=dict(symbol="star", size=18, color="#7c3aed"),
                name="Load resultant",
            )
        )

    figure.update_layout(
        title=f"{load_case.name}: bespoke layout",
        height=650,
        xaxis_title="X coordinate (m)",
        yaxis_title="Y coordinate (m)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=90, b=20),
    )
    figure.update_yaxes(scaleanchor="x", scaleratio=1)
    return figure


if st.button("Check bespoke layout", type="primary", use_container_width=True):
    if len(piles) < 3 or piles[["X (m)", "Y (m)"]].isna().any().any():
        st.error("Enter at least three valid pile coordinates.")
        st.stop()
    if piles["Pile"].astype(str).duplicated().any():
        st.error("Pile names must be unique.")
        st.stop()
    if loads["Load"].astype(str).duplicated().any():
        st.error("Load component names must be unique.")
        st.stop()

    coordinates = piles[["X (m)", "Y (m)"]].to_numpy(dtype=float)
    try:
        pile_group = PileGroup(coordinates)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    cases = build_cases(loads, combinations, pile_group.centroid)
    limits = DesignLimits(
        compression_capacity=float(compression_capacity),
        tension_capacity=float(tension_capacity),
        min_spacing=float(pile_diameter * spacing_factor),
        max_width=float(plot_width),
        max_depth=float(plot_depth),
    )
    solution = evaluate_layout(
        coordinates,
        cases,
        limits,
        mode="Bespoke pile layout",
        regularity_weight=0.0,
    )
    st.session_state.bespoke_solution = solution
    st.session_state.bespoke_cases = cases
    st.session_state.bespoke_limits = limits
    st.session_state.bespoke_piles_used = piles.copy()
    st.session_state.bespoke_core = (core_x, core_y)


if "bespoke_solution" in st.session_state:
    solution = st.session_state.bespoke_solution
    cases = st.session_state.bespoke_cases
    limits = st.session_state.bespoke_limits
    piles_used = st.session_state.bespoke_piles_used

    if solution.feasible:
        st.success("The bespoke layout satisfies the selected checks.")
    else:
        st.error("The bespoke layout fails one or more selected checks.")

    metrics = st.columns(5)
    metrics[0].metric("Pile count", solution.number_of_piles)
    metrics[1].metric("Maximum compression", f"{solution.max_compression:.0f} kN")
    metrics[2].metric("Maximum tension", f"{solution.max_tension:.0f} kN")
    metrics[3].metric("Gravity reserve", f"{solution.gravity_reserve:.2f}")
    metrics[4].metric("Minimum spacing", f"{solution.minimum_spacing:.2f} m")

    selected_case_name = st.selectbox(
        "Combination shown on the pile plot",
        [case.name for case in cases],
    )
    selected_case = next(case for case in cases if case.name == selected_case_name)
    st.plotly_chart(
        bespoke_figure(solution, selected_case, limits, piles_used),
        use_container_width=True,
    )

    reaction_table = pd.DataFrame(solution.reactions_by_case)
    reaction_table.insert(0, "Pile", piles_used["Pile"].astype(str).tolist())
    coordinate_table = piles_used[["Pile", "X (m)", "Y (m)"]].copy()

    coordinates_tab, reactions_tab, checks_tab = st.tabs(
        ["Coordinates", "Reactions", "Checks"]
    )
    with coordinates_tab:
        st.dataframe(coordinate_table, hide_index=True, use_container_width=True)
        st.download_button(
            "Download bespoke coordinates",
            coordinate_table.to_csv(index=False).encode("utf-8"),
            "bespoke_pile_coordinates.csv",
            "text/csv",
        )
    with reactions_tab:
        st.dataframe(reaction_table, hide_index=True, use_container_width=True)
        st.download_button(
            "Download bespoke reactions",
            reaction_table.to_csv(index=False).encode("utf-8"),
            "bespoke_pile_reactions.csv",
            "text/csv",
        )
    with checks_tab:
        st.write(
            f"Governing compression combination: "
            f"**{solution.governing_compression_case or 'Not applicable'}**"
        )
        st.write(
            f"Governing tension combination: "
            f"**{solution.governing_tension_case or 'Not applicable'}**"
        )
        for message in solution.messages:
            st.write(f"- {message}")
