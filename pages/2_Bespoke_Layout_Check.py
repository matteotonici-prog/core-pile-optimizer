import pandas as pd
import streamlit as st
from models import DesignLimits
from pilegroup import PileGroup
from analysis import create_cases,evaluate
from shared_ui import load_combination_tabs
from plotting import make_figure
st.title('Page 2 - Bespoke Pile Layout Check')
st.write('Enter the engineer-defined pile coordinates and the global coordinates of the core centre. The kern is always plotted.')
loads,combos=load_combination_tabs('bespoke')
if 'manual_piles' not in st.session_state:st.session_state.manual_piles=pd.DataFrame([{'Pile':'P1','X (m)':-4.,'Y (m)':-3.},{'Pile':'P2','X (m)':0.,'Y (m)':-3.},{'Pile':'P3','X (m)':4.,'Y (m)':-3.},{'Pile':'P4','X (m)':-4.,'Y (m)':3.},{'Pile':'P5','X (m)':0.,'Y (m)':3.},{'Pile':'P6','X (m)':4.,'Y (m)':3.}])
st.subheader('Bespoke pile coordinates')
piles=st.data_editor(st.session_state.manual_piles,num_rows='dynamic',hide_index=True,use_container_width=True,key='manual_pile_editor');st.session_state.manual_piles=piles
if st.button('＋ Add pile'):
 st.session_state.manual_piles=pd.concat([piles,pd.DataFrame([{'Pile':f'P{len(piles)+1}','X (m)':0.,'Y (m)':0.}])],ignore_index=True);st.rerun()
a,b,c=st.columns(3)
with a:core_x=st.number_input('Core centre X (m)',value=0.);core_y=st.number_input('Core centre Y (m)',value=0.)
with b:compression=st.number_input('Compression capacity (kN)',value=2500.);tension=st.number_input('Tension capacity (kN)',value=300.)
with c:diameter=st.number_input('Pile diameter (m)',value=.9);factor=st.number_input('Minimum spacing / diameter',value=3.);maxw=st.number_input('Plot X extent (m)',value=16.);maxd=st.number_input('Plot Y extent (m)',value=12.)
st.caption('Moments entered in Loads are about the core centre. Axial load eccentricity from core centre to pile-group centroid is transferred automatically: Mx += N dy and My += N dx.')
if st.button('Check bespoke pile layout',type='primary',use_container_width=True):
 if piles[['X (m)','Y (m)']].isna().any().any() or len(piles)<3:st.error('Enter at least three valid pile coordinates.');st.stop()
 coords=piles[['X (m)','Y (m)']].to_numpy(float)
 try:centroid=PileGroup(coords).centroid
 except ValueError as e:st.error(str(e));st.stop()
 limits=DesignLimits(compression,tension,diameter*factor,maxw,maxd);cases=create_cases(loads,combos,core_x,core_y,centroid);s=evaluate(coords,cases,limits,'Bespoke layout',require_envelope=False)
 if not s:st.error('The layout fails one or more selected capacity, tension or spacing checks.');st.stop()
 st.session_state.manual_solution=s;st.session_state.manual_cases=cases;st.session_state.manual_limits=limits;st.session_state.manual_core=(core_x,core_y)
if 'manual_solution' in st.session_state:
 s=st.session_state.manual_solution;cases=st.session_state.manual_cases;limits=st.session_state.manual_limits;core_x,core_y=st.session_state.manual_core
 m=st.columns(5);m[0].metric('Piles',s.number_of_piles);m[1].metric('Max compression',f'{s.max_compression:.0f} kN');m[2].metric('Max tension',f'{s.max_tension:.0f} kN');m[3].metric('Gravity reserve',f'{s.gravity_reserve:.2f}');m[4].metric('Minimum spacing',f'{s.minimum_spacing:.2f} m')
 lc=next(x for x in cases if x.name==st.selectbox('Combination shown',[x.name for x in cases]));st.plotly_chart(make_figure(s,lc,limits,core_x,core_y),use_container_width=True)
 coords=pd.DataFrame(s.coordinates,columns=['X (m)','Y (m)']);coords.insert(0,'Pile',[f'P{i+1}' for i in range(len(coords))]);react=pd.DataFrame(s.reactions_by_case);react.insert(0,'Pile',coords['Pile']);t1,t2=st.tabs(['Coordinates','Reactions'])
 with t1:st.dataframe(coords,hide_index=True,use_container_width=True);st.download_button('Download coordinates',coords.to_csv(index=False),'bespoke_pile_coordinates.csv')
 with t2:st.dataframe(react,hide_index=True,use_container_width=True);st.download_button('Download reactions',react.to_csv(index=False),'bespoke_pile_reactions.csv')
