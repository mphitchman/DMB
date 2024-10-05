import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px

st.set_page_config(layout="wide")


### load tables
@st.cache_data
def load_hit():
    return(pd.read_csv("https://mphitchman.com/DMB/csv/hit24_summary.csv"))
hit = load_hit()
#hit columns: 
#['Name', 'Pos', 'Age', 'PA', 'R', 'RBI', '2B', 'HR', 'SB', 'CS', 'BBpct','Kpct', 
#'RC27', 'OPS', 'XWOBA', 'O', 'Def', 'BsR', 'WAR', 'wRC+','RJML', 'SSBL', 'CJPL',
# 'key_FG', 'avgL', 'obpL', 'slgL', 'opsL','avgR', 'obpR', 'slgR', 'opsR']
#selected columns here:
select_hit_cols = ['Name','Pos','Age','PA','R','RBI','HR','SB','obpL',
                   'slgL','obpR','slgR','XWOBA','BBpct','Kpct','RC27','Def','BsR','WAR']
hit['Pos'] = hit['Pos'].replace(",","",regex=True) #streamlit introduces commas for integers > 999

@st.cache_data
def load_pit():
    return(pd.read_csv("https://mphitchman.com/DMB/csv/pit24_summary.csv"))
pit = load_pit()
#pit columns:
#['Unnamed: 0', 'Name', 'G', 'GS', 'TBF', 'W', 'L', 'SV', 'ERA', 'WHIP',
#       'RC27', 'OPS', 'XWOBA', 'xFIP', 'k%', 'bb%', 'k-bb%', 'gb%', 'hr9',
#       'WAR', 'RJML', 'SSBL', 'CJPL', 'key_FG', 'avgL', 'obpL', 'slgL', 'opsL',
#       'avgR', 'obpR', 'slgR', 'opsR']

select_pit_cols = ['Name', 'G', 'GS', 'TBF', 'ERA', 'WHIP', 'RC27', 'XWOBA','k%','bb%','gb%', 'hr9', 'obpL', 'slgL', 'obpR','slgR','WAR']

######

##########################################@
### Streamlit Page Build ###
###########################################



selected_league = st.selectbox(label='Select a DMB League',options = ['RJML','SSBL','CJPL'],index=0)

if selected_league == "RJML":
     my_team = "VAN"
elif selected_league == "SSBL":
     my_team = "NB"
elif selected_league =="CJPL":
     my_team = "OBS"

st.header("MLB'24 Stats for "+selected_league+" Teams",divider = 'blue')


#get nice teams list for selectboxes
teams = hit[hit[selected_league].notna()][selected_league].unique().tolist()
teams.sort()


col1, col2 = st.columns([2,10])

with col1:
    selected_team = st.selectbox("Select a team",teams,index=teams.index(my_team))
    #st.write("Complete MLB24 Season")
    #if we want clear cache button...
    # st.write("To check for updates, click button at bottom of page, then reload browser.)")

    hit_tm = hit[hit[selected_league]==selected_team]
    pit_tm = pit[pit[selected_league]==selected_team]
        
with col2:
    tab1,tab2 = st.tabs(['Hitting','Pitching'])
    with tab1:
        st.header(selected_team+' - Hitting')
        st.dataframe(
            hit_tm[select_hit_cols],
            column_config={
                #"avg": st.column_config.NumberColumn(format="%.3f"),
                #"obpR": st.column_config.NumberColumn(format="%.3f"),
                #"opsL": st.column_config.NumberColumn(format="%.3f"),
                "OPS": st.column_config.NumberColumn(format="%.3f"),
                "XWOBA": st.column_config.NumberColumn(format="%.3f"),
                "RC27": st.column_config.NumberColumn(format="%.1f"),
                "WAR": st.column_config.NumberColumn(format="%.1f"),
                "Def": st.column_config.NumberColumn(format="%.1f"),
                "BsR": st.column_config.NumberColumn(format="%.1f"),
            }
        )
    with tab2:
        st.header(selected_team+' - Pitching')
        st.dataframe(
            pit_tm[select_pit_cols],
            column_config={
                "ERA": st.column_config.NumberColumn(format="%.2f"),
                "XWOBA": st.column_config.NumberColumn(format="%.3f"),
                "WHIP": st.column_config.NumberColumn(format="%.2f"),
                "WAR": st.column_config.NumberColumn(format="%.1f"),
                "RC27": st.column_config.NumberColumn(format="%.1f"),
                "hr9": st.column_config.NumberColumn(format="%.1f"),
                "obpL": st.column_config.NumberColumn(format="%.3f"),
                "slgL": st.column_config.NumberColumn(format="%.3f"),
                "obpR": st.column_config.NumberColumn(format="%.3f"),
                "slgR": st.column_config.NumberColumn(format="%.3f")
            }
        )
        
    
    
