# Core Pile Layout Optimiser

A Streamlit concept-design tool that searches for pile layouts beneath structural cores.

## Two optimisation modes

1. **Force regular pile grid**
   - Searches centred rectangular full grids.
   - Optionally searches perimeter-only rectangular grids.
   - Varies spacing independently in X and Y.

2. **Allow free pile locations**
   - Uses a custom genetic search.
   - Every pile has an independent X and Y coordinate.
   - Enforces the maximum footprint and minimum centre-to-centre distance.
   - Allows a constructability preference without forcing a grid.

## Engineering model

The app assumes:

- A rigid pile cap.
- Equal axial stiffness for every pile.
- Positive axial load means compression.
- Positive Mx adds compression at positive Y.
- Positive My adds compression at positive X.
- Gravity load cases must keep all piles in compression.
- Wind/non-gravity load cases may use the entered tension capacity.

For irregular layouts, the full coupled pile-group geometry matrix is solved, including the `sum(x*y)` term.

## Important limitation

This is a preliminary layout optimiser, not a final foundation design tool. It does not currently include:

- Different pile axial stiffnesses.
- P-y interaction or soil springs.
- Pile-group geotechnical effects.
- Pile-cap bending, shear, punching or strut-and-tie design.
- Core-wall load introduction.
- Accidental eccentricity.
- Construction tolerances.
- Code-specific load combinations or partial factors.

All inputs and outputs must be checked by a suitably qualified engineer.

## Run on Streamlit Community Cloud

1. Create a new GitHub repository.
2. Upload all files from this project to the repository root.
3. Commit the files.
4. Open Streamlit Community Cloud.
5. Select the repository and branch.
6. Set the main file path to `app.py`.
7. Deploy.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate the virtual environment with:

```text
.venv\Scripts\activate
```

## Suggested first settings

- Optimisation mode: regular grid first.
- Then switch to free pile locations.
- Free search population: 60.
- Generations: 80.
- Keep the pile-count range narrow for faster runs, for example 18 to 24.
- Use both positive and negative wind directions.

## Files

- `app.py`: Streamlit interface.
- `models.py`: data classes.
- `pilegroup.py`: reaction analysis and geometry utilities.
- `evaluator.py`: constraints and scoring.
- `layouts.py`: regular and free-layout seeds.
- `optimizer_regular.py`: regular-grid search.
- `optimizer_free.py`: genetic free-location search.
- `plotting.py`: Plotly plan and reaction display.
