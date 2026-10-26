import pandas as pd
import streamlit as st

def initialise_state():
    if 'loads_df' not in st.session_state:st.session_state.loads_df=pd.DataFrame([{'Load':'Dead','N (kN)':32000.,'Mx (kNm)':10000.,'My (kNm)':7000.},{'Load':'Live','N (kN)':8000.,'Mx (kNm)':5000.,'My (kNm)':3000.},{'Load':'Wx','N (kN)':0.,'Mx (kNm)':35000.,'My (kNm)':2000.},{'Load':'Wy','N (kN)':0.,'Mx (kNm)':2000.,'My (kNm)':40000.}])
    if 'combos_df' not in st.session_state:st.session_state.combos_df=pd.DataFrame([{'Combination':'D + L','Check':'No tension','Dead':1.,'Live':1.,'Wx':0.,'Wy':0.},{'Combination':'D + L + Wx','Check':'Compression','Dead':1.,'Live':1.,'Wx':1.,'Wy':0.},{'Combination':'D + L + Wy','Check':'Compression','Dead':1.,'Live':1.,'Wx':0.,'Wy':1.},{'Combination':'0.9D + Wx','Check':'Tension','Dead':.9,'Live':0.,'Wx':1.,'Wy':0.},{'Combination':'0.9D + Wy','Check':'Tension','Dead':.9,'Live':0.,'Wx':0.,'Wy':1.}])

def load_combination_tabs(key):
    initialise_state(); t1,t2=st.tabs(['Loads','Combinations'])
    with t1:
        loads=st.data_editor(st.session_state.loads_df,num_rows='dynamic',hide_index=True,use_container_width=True,key=f'loads_{key}')
        if st.button('＋ Add load component',key=f'add_load_{key}'):
            st.session_state.loads_df=pd.concat([loads,pd.DataFrame([{'Load':f'Load {len(loads)+1}','N (kN)':0.,'Mx (kNm)':0.,'My (kNm)':0.}])],ignore_index=True);st.rerun()
        st.session_state.loads_df=loads
    with t2:
        names=[str(x) for x in loads['Load']]; combos=st.session_state.combos_df.copy()
        for n in names:
            if n not in combos:combos[n]=0.
        combos=combos[[c for c in ['Combination','Check']+names if c in combos]]
        combos=st.data_editor(combos,num_rows='dynamic',hide_index=True,use_container_width=True,key=f'combos_{key}',column_config={'Check':st.column_config.SelectboxColumn(options=['Compression','Tension','No tension'],required=True)})
        if st.button('＋ Add combination',key=f'add_combo_{key}'):
            st.session_state.combos_df=pd.concat([combos,pd.DataFrame([{'Combination':f'Combination {len(combos)+1}','Check':'Compression',**{n:0. for n in names}}])],ignore_index=True);st.rerun()
        st.session_state.combos_df=combos
    return loads,combos
