# Core Pile Optimiser v4

A Streamlit multipage application.

- Page 1: regular candidate pile-layout search.
- Page 2: bespoke engineer-defined pile coordinates and free core-centre coordinates.
- Loads and combinations are shared through Streamlit session state.
- The exact discrete pile-group no-tension kern is always plotted on both pages.
- On Page 2, load-component moments are entered about the core centre. The axial load is transferred to the pile-group centroid using `Mx += N*dy` and `My += N*dx`.

Upload all files and the `pages` folder to a GitHub repository. Deploy `app.py` on Streamlit Community Cloud.

This is a preliminary rigid-cap, equal-pile-stiffness tool. It does not replace pile, pile-cap, geotechnical group or soil-structure interaction design.
