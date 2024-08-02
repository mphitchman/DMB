import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px
from bs4 import BeautifulSoup
import requests 
import re
from datetime import datetime
from io import StringIO

st.set_page_config(layout="wide")


## load keyID
@st.cache_data
def load_key():
    return(pd.read_csv("https://mphitchman.com/DMB/csv/keyID.csv"))

keyID = load_key()


def extract_id(string):
    if 'mlb_ID' in string:
        id=re.findall(r'\d+',string)[1]
    else:
        id = ""
    return(id)

def rates(df):
    '''df must have these columns: 'AB', 'H','2B','3B','HR','BB','HBP','SF','PA','SO' '''
    df['avg'] = round(df['H']/df['AB'],3)
    df['obp'] = round((df['H']+df['BB']+df['HBP'])/(df['AB']+df['BB']+df['HBP']+df['SF']),3)
    df['slg'] = round((df['H']+df['2B']+2*df['3B']+3*df['HR'])/df['AB'],3)
    df['ops'] = round(df['obp']+df['slg'],3)
    df['bb%'] = round(df['BB']/df['PA']*100,1)
    df['k%'] = round(df['SO']/df['PA']*100,1)
    return(df)

hit_columns = ['Name','O','PA','AB','H','2B','3B','HBP','SF','HR','R','RBI','BB','SO','SB']

def team_log(tm,lg):
    table = df[df[lg]==tm][hit_columns]
    table.loc['Total'] = table.sum()
    table.loc[table.index[-1], 'Name'] = 'Total'
    table = rates(table)[['Name','O','PA','H','2B','3B','HR','R','RBI','SB','BB','SO','avg','obp','slg','ops']]
    return(table)

def load_gamelog():
    date = dt.datetime.today().strftime('%Y-%m-%d')
    st_date = dt.datetime.today().replace(day=1).strftime('%Y-%m-%d')
    game_date = (dt.datetime.today()+dt.timedelta(days=-1)).strftime('%Y-%m-%d')
    url = "https://www.baseball-reference.com/leagues/daily.fcgi?request=1&type=b&dates=yesterday&lastndays=7&since="+st_date+"&fromandto="+st_date+"."+date+"&level=mlb&franch=ANY"
    response = requests.get(url)
    html = response.text
    # Create the soup object
    soup = BeautifulSoup(html, "lxml")
    # extract the table
    table = soup.find_all('table', {'class': 'sortable stats_table'})[0]
    headers = []
    rows = []
    for i, row in enumerate(table.find_all('tr')):
        if i == 0:
            headers = [el.text.strip() for el in row.find_all('th')]
        else:
            rows.append([el.text.strip() for el in row.find_all('td')])
    # create and clean the dataframe
    df = pd.read_html(StringIO(str(table)))[0]
    df = df[df['Name'] != 'Name']
    num_cols = ['PA','AB','H','2B','3B','HR','R','RBI','SB','CS','BB','IBB','HBP','SO','SH','SF','GDP']
    df[num_cols] = df[num_cols].apply(pd.to_numeric)
    def add_O(df):
        df['O'] = df['H']+df['2B']+2*df['3B']+2*df['HR']+df['BB']+df['SB']+df['SH']+df['R'] + df['RBI']-df['CS']-df['GDP']
        return(df)
    df = add_O(df)
    df.drop(['Rk','Unnamed: 2', 'Unnamed: 3', 'Lev'], axis=1, inplace=True)
    df = df.rename(columns = {'Unnamed: 7':'H/A'})
    links = table.find_all('a', href=True)
    m = int(len(links)/3)
    key_MLB = [""]*m
    for k in range(m):
        i = 3*k
        key_MLB[k] = int(extract_id(links[i]['href'])) 
    df['key_MLB'] = key_MLB
    df['date'] = game_date
    keyID = pd.read_csv('csv/keyID.csv')
    df = df.merge(keyID[keyID['type']=="B"][['type','key_MLB','RJML','SSBL','CJPL']],on="key_MLB",how='left')
    return(df)
    
df = load_gamelog()

######

##########################################@
### Streamlit Page Build ###
###########################################

date = dt.datetime.today().strftime('%Y-%m-%d')
game_date = (dt.datetime.today()+dt.timedelta(days=-1)).strftime('%Y-%m-%d')

selected_league = st.selectbox(label='Select a DMB League',options = ['RJML','SSBL','CJPL'],index=0)

if selected_league == "RJML":
     my_team = "VAN"
elif selected_league == "SSBL":
     my_team = "NB"
elif selected_league =="CJPL":
     my_team = "OBS"

st.header("Yesterday's Hitting Game Logs for "+selected_league+" Teams",divider = 'blue')


#get nice teams list for selectboxes
teams = hit24[hit24[selected_league].notna()][selected_league].unique().tolist()
teams.sort()
teams.remove('avail')
teams = teams+['Team Totals']


col1, col2 = st.columns([2,10])

with col1:
    selected_team = st.selectbox("Select a team",teams,index=teams.index(my_team))
    
    #if we want clear cache button...
    # st.write("To check for updates, click button at bottom of page, then reload browser.)")

    if selected_team == "Team Totals":
        team_hit_gl = rates(df[[lg]+num_cols].groupby(lg).sum())[['O','PA','H','HR','R','RBI','BB','SO','SB','avg','obp','slg','ops']].sort_values(by=["ops",'O','HR','R'],ascending=False)
        
    elif selected_team != "Team Totals":
        team_hit_gl = team_log(lg=selected_league,tm=selected_team)
        
with col2:
    tab1,tab2 = st.tabs(['Hitting','Pitching'])
    with tab1:
        st.header(selected_team+' - Hitting')
        st.dataframe(
            team_hit_gl,
            column_config={
                "avg": st.column_config.NumberColumn(format="%.3f"),
                "obp": st.column_config.NumberColumn(format="%.3f"),
                "slg": st.column_config.NumberColumn(format="%.3f"),
                "ops": st.column_config.NumberColumn(format="%.3f"),
            }
        )
    with tab2:
        st.header(selected_team+' - Pitching')
        st.dataframe(
            team_pit_gl = pd.DataFrame({'x':['a','b','c']}),
        )  

#if st.button("Clear cache"):
 #           st.cache_data.clear()