import pandas as pd
import streamlit as st
from models import DesignLimits
from analysis import create_cases,evaluate
from layouts import grid
from shared_ui import load_combination_tabs
from plotting import make_figure
st.title('Page 1 - Optimised Layout')
loads,combos=load_combination_tabs('optimised')
a,b=st.columns(2)
with a:compression=st.number_input('Compression capacity (kN)',value=2500.);tension=st.number_input('Tension capacity (kN)',value=300.);diameter=st.number_input('Pile diameter (m)',value=.9);factor=st.number_input('Minimum spacing / diameter',value=3.)
with b:maxw=st.number_input('Maximum X extent (m)',value=16.);maxd=st.number_input('Maximum Y extent (m)',value=12.);minp=st.number_input('Minimum piles',3,18);maxp=st.number_input('Maximum piles',int(minp),24);maxresults=st.number_input('Maximum results',1,20,5)
if st.button('Run regular-grid search',type='primary'):
 limits=DesignLimits(compression,tension,diameter*factor,maxw,maxd);found=[];cases=create_cases(loads,combos)
 for nx in range(2,int(maxw//limits.min_spacing)+2):
  for ny in range(2,int(maxd//limits.min_spacing)+2):
   p=grid(nx,ny,limits.min_spacing,limits.min_spacing)
   if minp<=len(p)<=maxp:
    s=evaluate(p,cases,limits,'Regular grid')
    if s:found.append(s)
 found=sorted(found,key=lambda x:x.score)[:maxresults]
 if not found:st.error('No feasible layout found.');st.stop()
 st.session_state.opt_results=found;st.session_state.opt_cases=cases;st.session_state.opt_limits=limits
if 'opt_results' in st.session_state:
 results=st.session_state.opt_results;cases=st.session_state.opt_cases;limits=st.session_state.opt_limits
 st.dataframe(pd.DataFrame([{'Rank':i+1,'Piles':s.number_of_piles,'Max compression':round(s.max_compression,1),'Max tension':round(s.max_tension,1),'Score':round(s.score,2)} for i,s in enumerate(results)]),hide_index=True,use_container_width=True)
 s=results[st.selectbox('Result',range(1,len(results)+1))-1];lc=next(x for x in cases if x.name==st.selectbox('Combination',[x.name for x in cases]));st.plotly_chart(make_figure(s,lc,limits),use_container_width=True)
