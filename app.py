import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from optimizer import run_optimization

st.set_page_config(
    page_title="Core Pile Optimizer",
    layout="wide"
)

st.title(
    "Core Pile Layout Optimizer"
)

st.sidebar.header("Gravity Load")

N_gq = st.sidebar.number_input(
    "N DL+LL (kN)",
    value=40000.0
)

Mx_gq = st.sidebar.number_input(
    "Mx DL+LL (kNm)",
    value=15000.0
)

My_gq = st.sidebar.number_input(
    "My DL+LL (kNm)",
    value=10000.0
)

st.sidebar.header("Wind X")

N_wx = st.sidebar.number_input(
    "N Wind X",
    value=40000.0
)

Mx_wx = st.sidebar.number_input(
    "Mx Wind X",
    value=50000.0
)

My_wx = st.sidebar.number_input(
    "My Wind X",
    value=10000.0
)

st.sidebar.header("Wind Y")

N_wy = st.sidebar.number_input(
    "N Wind Y",
    value=40000.0
)

Mx_wy = st.sidebar.number_input(
    "Mx Wind Y",
    value=10000.0
)

My_wy = st.sidebar.number_input(
    "My Wind Y",
    value=50000.0
)

st.sidebar.header("Pile Data")

compression_capacity = st.sidebar.number_input(
    "Compression Capacity per Pile (kN)",
    value=2500.0
)

tension_capacity = st.sidebar.number_input(
    "Tension Capacity per Pile (kN)",
    value=0.0
)

spacing = st.sidebar.number_input(
    "Pile Spacing (m)",
    value=2.7
)

st.sidebar.header("Pile Cap Limits")

max_width = st.sidebar.number_input(
    "Max Width (m)",
    value=16.0
)

max_depth = st.sidebar.number_input(
    "Max Depth (m)",
    value=16.0
)

loadcases = [

    {
        "name":"Gravity",
        "N":N_gq,
        "Mx":Mx_gq,
        "My":My_gq
    },

    {
        "name":"Wind X",
        "N":N_wx,
        "Mx":Mx_wx,
        "My":My_wx
    },

    {
        "name":"Wind Y",
        "N":N_wy,
        "Mx":Mx_wy,
        "My":My_wy
    }
]

if st.button("Run Optimisation"):

    results = run_optimization(
        loadcases,
        compression_capacity,
        tension_capacity,
        max_width,
        max_depth,
        spacing
    )

    if len(results) == 0:
        st.error("No valid layouts found")

    else:

        best = results[0]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Piles",
            best["n_piles"]
        )

        c2.metric(
            "Area (m²)",
            round(best["area"],1)
        )

        c3.metric(
            "Max Compression",
            round(best["max_compression"],0)
        )

        c4.metric(
            "Max Tension",
            round(best["max_tension"],0)
        )

        fig = go.Figure()

        x = [p[0] for p in best["layout"]]
        y = [p[1] for p in best["layout"]]

        fig.add_trace(

            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                marker=dict(
                    size=14,
                    color="red"
                ),
                name="Piles"
            )
        )

        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        table = []

        for i, r in enumerate(results[:20]):

            table.append({

                "Rank": i + 1,
                "Piles": r["n_piles"],
                "Area": round(r["area"], 1),
                "Compression":
                round(
                    r["max_compression"],1
                ),
                "Tension":
                round(
                    r["max_tension"],1
                ),
                "Score":
                round(
                    r["score"],1
                )
            })

        st.subheader(
            "Top 20 Solutions"
        )

        st.dataframe(
            pd.DataFrame(table),
            use_container_width=True
        )
