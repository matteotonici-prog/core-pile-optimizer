import pandas as pd
import streamlit as st
from models import LoadCase, DesignLimits
from optimizer_regular import optimise_regular
from optimizer_free import optimise_free
from plotting import make_figure

st.set_page_config(page_title="Core Pile Optimiser",layout="wide")
st.title("Core Pile Layout Optimiser")
st.caption("Concept-stage rigid-cap optimisation with regular-grid and free-location modes.")

if "loads_df" not in st.session_state:
    st.session_state.loads_df=pd.DataFrame([
        {"Load":"Dead","N (kN)":32000.0,"Mx (kNm)":10000.0,"My (kNm)":7000.0},
        {"Load":"Live","N (kN)":8000.0,"Mx (kNm)":5000.0,"My (kNm)":3000.0},
        {"Load":"Wx","N (kN)":0.0,"Mx (kNm)":35000.0,"My (kNm)":2000.0},
        {"Load":"Wy","N (kN)":0.0,"Mx (kNm)":2000.0,"My (kNm)":40000.0},])
if "combos_df" not in st.session_state:
    st.session_state.combos_df=pd.DataFrame([
        {"Combination":"D + L","Check":"No tension","Dead":1.0,"Live":1.0,"Wx":0.0,"Wy":0.0},
        {"Combination":"D + L + Wx","Check":"Compression","Dead":1.0,"Live":1.0,"Wx":1.0,"Wy":0.0},
        {"Combination":"D + L + Wy","Check":"Compression","Dead":1.0,"Live":1.0,"Wx":0.0,"Wy":1.0},
        {"Combination":"0.9D + Wx","Check":"Tension","Dead":0.9,"Live":0.0,"Wx":1.0,"Wy":0.0},
        {"Combination":"0.9D + Wy","Check":"Tension","Dead":0.9,"Live":0.0,"Wx":0.0,"Wy":1.0},])

tab_loads,tab_combos=st.tabs(["Loads","Combinations"])
with tab_loads:
    st.subheader("Load components")
    st.write("Enter signed axial load and overturning moments for Dead, Live, Wx and Wy.")
    loads=st.data_editor(st.session_state.loads_df,num_rows="dynamic",hide_index=True,use_container_width=True,key="loads_editor")
    if st.button("＋ Add load component",key="add_load"):
        loads=pd.concat([loads,pd.DataFrame([{"Load":f"Load {len(loads)+1}","N (kN)":0.0,"Mx (kNm)":0.0,"My (kNm)":0.0}])],ignore_index=True)
        st.session_state.loads_df=loads; st.rerun()
    st.session_state.loads_df=loads
with tab_combos:
    st.subheader("Load combinations")
    st.write("Each factor column multiplies the corresponding load component. Select which limit the combination checks.")
    load_names=[str(x) for x in loads["Load"].tolist()]
    combos=st.session_state.combos_df.copy()
    for name in load_names:
        if name not in combos.columns: combos[name]=0.0
    base=["Combination","Check"]+load_names
    combos=combos[[c for c in base if c in combos.columns]]
    combos=st.data_editor(combos,num_rows="dynamic",hide_index=True,use_container_width=True,key="combos_editor",column_config={"Check":st.column_config.SelectboxColumn(options=["Compression","Tension","No tension"],required=True)})
    if st.button("＋ Add combination",key="add_combo"):
        row={"Combination":f"Combination {len(combos)+1}","Check":"Compression",**{n:0.0 for n in load_names}}
        combos=pd.concat([combos,pd.DataFrame([row])],ignore_index=True); st.session_state.combos_df=combos; st.rerun()
    st.session_state.combos_df=combos

st.divider()
a,b,c=st.columns(3)
with a:
    st.subheader("Pile limits")
    compression=st.number_input("Compression capacity per pile (kN)",1.0,value=2500.0)
    tension=st.number_input("Tension capacity per pile (kN)",0.0,value=300.0)
    diameter=st.number_input("Pile diameter (m)",0.1,value=.9)
    spacing_factor=st.number_input("Minimum spacing / diameter",1.0,value=3.0)
with b:
    st.subheader("Search envelope")
    max_width=st.number_input("Maximum X extent (m)",1.0,value=16.0)
    max_depth=st.number_input("Maximum Y extent (m)",1.0,value=12.0)
    min_piles=st.number_input("Minimum piles",3,value=18,step=1)
    max_piles=st.number_input("Maximum piles",int(min_piles),value=max(24,int(min_piles)),step=1)
    max_results=st.number_input("Maximum results to create",1,20,5,help="The free search stops when this number of feasible solutions has been found.")
with c:
    st.subheader("Optimisation")
    mode=st.radio("Pile locations",["Force regular pile grid","Allow free pile locations"])
    if mode=="Force regular pile grid":
        spacing_steps=st.slider("Spacing variations",2,6,4); include_perimeter=st.checkbox("Include perimeter grids",True)
    else:
        population=st.slider("Population",10,80,30,5); generations=st.slider("Maximum generations",10,100,35,5); patience=st.slider("Stop after generations without improvement",3,30,10); mutation=st.slider("Movement size",.1,.8,.3,.05); regularity=st.slider("Constructability preference",0.0,1.0,.2,.05); seed=st.number_input("Random seed",0,value=42)

if st.button("Run optimisation",type="primary",use_container_width=True):
    st.session_state.loads_df=loads; st.session_state.combos_df=combos
    if loads["Load"].duplicated().any(): st.error("Load component names must be unique."); st.stop()
    component={row["Load"]:row for _,row in loads.iterrows()}
    cases=[]
    for _,row in combos.iterrows():
        n=mx=my=0.0
        for name in load_names:
            factor=float(row.get(name,0.0)); n+=factor*float(component[name]["N (kN)"]); mx+=factor*float(component[name]["Mx (kNm)"]); my+=factor*float(component[name]["My (kNm)"])
        cases.append(LoadCase(str(row["Combination"]),n,mx,my,str(row["Check"])))
    if not any(x.check_type=="Compression" for x in cases) or not any(x.check_type=="Tension" for x in cases): st.error("Provide at least one Compression and one Tension combination."); st.stop()
    limits=DesignLimits(compression,tension,diameter*spacing_factor,max_width,max_depth)
    with st.spinner("Searching layouts..."):
        if mode=="Force regular pile grid": results=optimise_regular(cases,limits,int(min_piles),int(max_piles),int(max_results),spacing_steps,include_perimeter)
        else:
            bar=st.progress(0.0,"Running fast free-location search")
            results=optimise_free(cases,limits,int(min_piles),int(max_piles),int(max_results),population,generations,patience,mutation,regularity,int(seed),lambda v:bar.progress(v,"Running fast free-location search")); bar.empty()
    if not results: st.error("No feasible layout found. Increase pile count, capacity or footprint, or increase search effort."); st.stop()
    st.session_state.results=results; st.session_state.cases=cases; st.session_state.limits=limits

if "results" in st.session_state:
    results=st.session_state.results; cases=st.session_state.cases; limits=st.session_state.limits
    st.subheader("Results")
    summary=pd.DataFrame([{"Rank":i+1,"Mode":s.mode,"Piles":s.number_of_piles,"Width":round(s.footprint_width,2),"Depth":round(s.footprint_depth,2),"Max compression":round(s.max_compression,1),"Max tension":round(s.max_tension,1),"Compression util.":round(s.compression_utilisation,3),"Tension util.":round(s.tension_utilisation,3),"Gravity reserve":round(s.gravity_reserve,3),"Score":round(s.score,2)} for i,s in enumerate(results)])
    st.dataframe(summary,hide_index=True,use_container_width=True)
    rank=st.selectbox("Result to inspect",range(1,len(results)+1)); s=results[rank-1]
    case_name=st.selectbox("Combination shown",[x.name for x in cases]); lc=next(x for x in cases if x.name==case_name)
    st.plotly_chart(make_figure(s,lc,limits),use_container_width=True)
    coords=pd.DataFrame(s.coordinates,columns=["X (m)","Y (m)"]); coords.insert(0,"Pile",[f"P{i+1}" for i in range(len(coords))])
    reactions=pd.DataFrame(s.reactions_by_case); reactions.insert(0,"Pile",coords["Pile"])
    t1,t2=st.tabs(["Coordinates","Reactions"])
    with t1: st.dataframe(coords,hide_index=True,use_container_width=True); st.download_button("Download coordinates",coords.to_csv(index=False),"pile_coordinates.csv")
    with t2: st.dataframe(reactions,hide_index=True,use_container_width=True); st.download_button("Download reactions",reactions.to_csv(index=False),"pile_reactions.csv")
