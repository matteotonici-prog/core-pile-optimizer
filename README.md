# Core Pile Optimiser v3

Streamlit concept tool for regular-grid and free-location pile layout optimisation.

## Main workflow

- **Loads tab:** enter Dead, Live, Wx and Wy as separate signed load components. Use **+ Add load component** for additional actions.
- **Combinations tab:** define editable factors and select `Compression`, `Tension`, or `No tension` for each combination.
- Default combinations are D+L, D+L+Wx, D+L+Wy, 0.9D+Wx and 0.9D+Wy.
- Set **Maximum results to create** to stop the free search when enough feasible alternatives have been found.

## Free-search speed

The free mode now uses smaller practical defaults, early stopping after no improvement, ascending pile-count search, and a hard maximum number of returned results. Keep the pile range narrow, e.g. 20 to 24, for quick preliminary studies.

## Deploy

Upload all files to the root of a GitHub repository. In Streamlit Community Cloud choose `app.py` as the main file.

## Engineering limitations

Rigid cap and equal pile axial stiffness are assumed. This is not pile-cap, pile structural, geotechnical group, or soil-structure interaction design. Check all results independently.
