This is an additive update for Core Pile Optimiser v3.

Do not replace app.py or any existing optimiser file.

1. Keep the existing project unchanged.
2. Copy the included pages folder into the repository root.
3. The final repository should contain:

   app.py
   evaluator.py
   models.py
   pilegroup.py
   plotting.py
   optimizer_free.py
   optimizer_regular.py
   layouts.py
   pages/
       2_Bespoke_Layout.py

4. This page requires the previous kern update, specifically the
   PileGroup.kern_polygon() method in pilegroup.py.
5. Deploy app.py as before. Streamlit will automatically show the new page
   in the sidebar.
