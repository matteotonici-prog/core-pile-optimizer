from __future__ import annotations

import pandas as pd
import streamlit as st

from models import DesignLimits, LoadCase
from optimizer_free import optimise_free
from optimizer_regular import optimise_regular
from plotting import layout_figure


st.set_page_config(page_title="Core Pile Optimiser", page_icon="🏗️", layout="wide")
st.title("Core Pile Layout Optimiser")
st.caption("Concept-stage rigid pile-cap optimisation for equal axial pile stiffnesses.")

with st.expander("Calculation basis and sign convention", expanded=False):
    st.markdown(
        """
- Positive **N** is compression.
- Positive **Mx** increases compression at positive **Y**.
- Positive **My** increases compression at positive **X**.
- Negative reaction means pile tension/uplift.
- Gravity cases must keep every pile in compression.
- Non-gravity cases may use the entered tension capacity.
- The reaction model assumes a rigid cap and equal axial pile stiffnesses. It does not design the pile cap or account for soil-structure interaction.
        """
    )

st.subheader("1. Load cases")
default_loads = pd.DataFrame(
    [
        {"Name": "G + Q", "N (kN)": 40000.0, "Mx (kNm)": 15000.0, "My (kNm)": 10000.0, "Gravity": True},
        {"Name": "Wind +X", "N (kN)": 40000.0, "Mx (kNm)": 50000.0, "My (kNm)": 12000.0, "Gravity": False},
        {"Name": "Wind +Y", "N (kN)": 40000.0, "Mx (kNm)": 12000.0, "My (kNm)": 50000.0, "Gravity": False},
        {"Name": "Wind -X", "N (kN)": 40000.0, "Mx (kNm)": -50000.0, "My (kNm)": -12000.0, "Gravity": False},
        {"Name": "Wind -Y", "N (kN)": 40000.0, "Mx (kNm)": -12000.0, "My (kNm)": -50000.0, "Gravity": False},
    ]
)
load_table = st.data_editor(default_loads, num_rows="dynamic", use_container_width=True, hide_index=True)

left, middle, right = st.columns(3)
with left:
    st.subheader("2. Pile limits")
    compression_capacity = st.number_input("Compression capacity per pile (kN)", min_value=1.0, value=2500.0, step=100.0)
    tension_capacity = st.number_input("Allowable tension per pile for non-gravity cases (kN)", min_value=0.0, value=300.0, step=50.0)
    pile_diameter = st.number_input("Pile diameter (m)", min_value=0.1, value=0.9, step=0.1)
    spacing_factor = st.number_input("Minimum spacing / pile diameter", min_value=1.0, value=3.0, step=0.25)
    min_spacing = pile_diameter * spacing_factor
    st.info(f"Minimum centre-to-centre spacing: **{min_spacing:.2f} m**")

with middle:
    st.subheader("3. Maximum footprint")
    max_width = st.number_input("Maximum X extent (m)", min_value=min_spacing, value=16.0, step=0.5)
    max_depth = st.number_input("Maximum Y extent (m)", min_value=min_spacing, value=12.0, step=0.5)
    min_piles = st.number_input("Minimum number of piles", min_value=3, value=12, step=1)
    max_piles = st.number_input("Maximum number of piles", min_value=int(min_piles), value=max(30, int(min_piles)), step=1)

with right:
    st.subheader("4. Optimisation mode")
    mode = st.radio(
        "Pile-location constraint",
        ["Force regular pile grid", "Allow free pile locations"],
        help="Regular mode searches full and perimeter rectangular grids. Free mode moves every pile independently.",
    )
    if mode == "Force regular pile grid":
        spacing_steps = st.slider("Spacing variations per direction", 2, 8, 5)
        include_perimeter = st.checkbox("Include perimeter-only grids", value=True)
    else:
        population = st.slider("Population per pile count", 20, 150, 60, step=10)
        generations = st.slider("Generations per pile count", 20, 250, 80, step=10)
        mutation_scale = st.slider("Movement size", 0.10, 1.00, 0.35, step=0.05)
        regularity_preference = st.slider(
            "Constructability preference",
            0.0,
            1.0,
            0.25,
            step=0.05,
            help="0 gives full geometric freedom. 1 applies a stronger preference for aligned pile locations, but does not force a grid.",
        )
        random_seed = st.number_input("Random seed", min_value=0, value=42, step=1)

run = st.button("Run optimisation", type="primary", use_container_width=True)

if run:
    if load_table.empty:
        st.error("Enter at least one load case.")
        st.stop()
    if not bool(load_table["Gravity"].astype(bool).any()):
        st.error("At least one load case must be marked as a gravity case.")
        st.stop()

    load_cases = [
        LoadCase(
            name=str(row["Name"]),
            n=float(row["N (kN)"]),
            mx=float(row["Mx (kNm)"]),
            my=float(row["My (kNm)"]),
            is_gravity=bool(row["Gravity"]),
        )
        for _, row in load_table.iterrows()
    ]
    limits = DesignLimits(
        compression_capacity=float(compression_capacity),
        tension_capacity=float(tension_capacity),
        min_spacing=float(min_spacing),
        max_width=float(max_width),
        max_depth=float(max_depth),
    )

    with st.spinner("Searching pile layouts..."):
        if mode == "Force regular pile grid":
            results = optimise_regular(
                load_cases,
                limits,
                int(min_piles),
                int(max_piles),
                spacing_steps=spacing_steps,
                include_perimeter=include_perimeter,
            )
        else:
            progress = st.progress(0.0, text="Running free-location genetic search")
            results = optimise_free(
                load_cases,
                limits,
                int(min_piles),
                int(max_piles),
                population_size=population,
                generations=generations,
                mutation_scale=mutation_scale,
                regularity_preference=regularity_preference,
                random_seed=int(random_seed),
                progress_callback=lambda value: progress.progress(value, text="Running free-location genetic search"),
            )
            progress.empty()

    if not results:
        st.error("No feasible layout was found. Increase the footprint or pile count/capacity, reduce spacing, or allow more free-search generations.")
        st.stop()

    st.session_state["results"] = results
    st.session_state["load_cases"] = load_cases
    st.session_state["limits"] = limits

if "results" in st.session_state:
    results = st.session_state["results"]
    load_cases = st.session_state["load_cases"]
    limits = st.session_state["limits"]

    st.subheader("5. Ranked solutions")
    summary = pd.DataFrame(
        [
            {
                "Rank": index + 1,
                "Mode": solution.mode,
                "Piles": solution.number_of_piles,
                "Width (m)": round(solution.footprint_width, 2),
                "Depth (m)": round(solution.footprint_depth, 2),
                "Area (m2)": round(solution.footprint_area, 2),
                "Max compression (kN)": round(solution.max_compression, 1),
                "Max tension (kN)": round(solution.max_tension, 1),
                "Compression util.": round(solution.max_compression_utilisation, 3),
                "Tension util.": round(solution.max_tension_utilisation, 3),
                "Gravity reserve": round(solution.gravity_reserve, 3),
                "Min spacing (m)": round(solution.minimum_spacing, 3),
                "Score": round(solution.score, 2),
            }
            for index, solution in enumerate(results[:20])
        ]
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)

    selected_rank = st.selectbox("Solution to inspect", options=list(range(1, min(20, len(results)) + 1)))
    selected = results[selected_rank - 1]
    selected_case_name = st.selectbox("Load case shown on plan", [case.name for case in load_cases])
    selected_case = next(case for case in load_cases if case.name == selected_case_name)

    metrics = st.columns(5)
    metrics[0].metric("Pile count", selected.number_of_piles)
    metrics[1].metric("Max compression", f"{selected.max_compression:.0f} kN")
    metrics[2].metric("Max tension", f"{selected.max_tension:.0f} kN")
    metrics[3].metric("Gravity reserve", f"{selected.gravity_reserve:.2f}")
    metrics[4].metric("Minimum spacing", f"{selected.minimum_spacing:.2f} m")

    st.plotly_chart(
        layout_figure(selected, selected_case, limits.max_width, limits.max_depth),
        use_container_width=True,
    )

    coordinates = pd.DataFrame(selected.coordinates, columns=["X (m)", "Y (m)"])
    coordinates.insert(0, "Pile", [f"P{i + 1}" for i in range(len(coordinates))])
    reactions = pd.DataFrame({name: values for name, values in selected.reactions_by_case.items()})
    reactions.insert(0, "Pile", coordinates["Pile"])

    tab1, tab2, tab3 = st.tabs(["Pile coordinates", "Pile reactions", "Checks"])
    with tab1:
        st.dataframe(coordinates, use_container_width=True, hide_index=True)
        st.download_button(
            "Download selected coordinates CSV",
            coordinates.to_csv(index=False).encode("utf-8"),
            "pile_coordinates.csv",
            "text/csv",
        )
    with tab2:
        st.dataframe(reactions, use_container_width=True, hide_index=True)
        st.download_button(
            "Download reactions CSV",
            reactions.to_csv(index=False).encode("utf-8"),
            "pile_reactions.csv",
            "text/csv",
        )
    with tab3:
        st.write(f"Governing compression case: **{selected.governing_compression_case}**")
        st.write(f"Governing tension case: **{selected.governing_tension_case}**")
        for message in selected.messages:
            st.write(f"- {message}")
