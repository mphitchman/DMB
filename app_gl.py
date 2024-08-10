import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests 
import re
import datetime as dt
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

def rates_pit(df):
    '''df must have these columns: ['IP','BF','AB','H','2B','3B','HR','ER','BB','SO','HBP','SF']'''
    import numpy as np
    df['Inn'] = np.floor(df['IP'])+10*(df['IP']-np.floor(df['IP']))/3
    df['avg'] = round(df['H']/df['AB'],3)
    df['obp'] = round((df['H']+df['BB']+df['HBP'])/(df['AB']+df['BB']+df['HBP']+df['SF']),3)
    df['slg'] = round((df['H']+df['2B']+2*df['3B']+3*df['HR'])/df['AB'],3)
    df['ops'] = df['obp']+df['slg']
    df['k%'] = round(df['SO']/df['BF']*100,1)
    df['bb%'] = round(df['BB']/df['BF']*100,1)
    df['hr9'] = round(df['HR']/df['Inn']*9,1)
    df['whip'] = round((df['BB']+df['H'])/df['Inn'],2)
    df['era'] = round(df['ER']/df['Inn']*9,2)
    df['babip'] = round((df['H']-df['HR'])/(df['AB']-df['HR']-df['SO']+df['SF']),3)
    df['k-bb%'] = df['k%']-df['bb%']
    return(df)



hit_columns = ['Name','O','PA','AB','H','2B','3B','HBP','SF','HR','R','RBI','BB','SO','SB']

def load_hit_gamelog():
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
   
hf = load_hit_gamelog()

def team_hit_log(tm,lg):
    table = hf[hf[lg]==tm][hit_columns]
    table.loc['Total'] = table.sum()
    table.loc[table.index[-1], 'Name'] = 'Total'
    table = rates(table)[['Name','O','PA','H','2B','3B','HR','R','RBI','SB','BB','SO','avg','obp','slg','ops']].set_index('Name')
    return(table)

def load_pit_gamelog():
    date = dt.datetime.today().strftime('%Y-%m-%d')
    st_date = dt.datetime.today().replace(day=1).strftime('%Y-%m-%d')
    game_date = (dt.datetime.today()+dt.timedelta(days=-1)).strftime('%Y-%m-%d')
    url = "https://www.baseball-reference.com/leagues/daily.fcgi?request=1&type=p&dates=yesterday&lastndays=7&since=2024-08-01&fromandto=2024-08-01.2024-08-31&level=mlb&franch=ANY"
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
    num_cols = ['GS', 'W', 'L', 'SV', 'IP', 'H', 'R', 'ER', 'BB','SO', 'HR', 'HBP', 'GSc','AB','2B','3B','IBB','GDP','SF','SB','CS', 'PO','BF']
    df[num_cols] = df[num_cols].apply(pd.to_numeric)
    df.drop(['Rk','Unnamed: 2', 'Unnamed: 3', 'Lev'], axis=1, inplace=True)
    df = df.rename(columns = {'Unnamed: 7':'H/A'})
    df['H/A']=df['H/A'].fillna(' ')
    links = table.find_all('a', href=True)
    m = int(len(links)/3)
    key_MLB = [""]*m
    for k in range(m):
        i = 3*k
        key_MLB[k] = int(extract_id(links[i]['href'])) 
    df['key_MLB'] = key_MLB
    df['date'] = game_date
    keyID = pd.read_csv('csv/keyID.csv')
    df = df.merge(keyID[keyID['type']=="P"][['type','key_MLB','RJML','SSBL','CJPL']],on="key_MLB",how='left')
    return(df)

pf = load_pit_gamelog()


def team_pit_log(tm,lg):
    pit_columns = ['Name','H/A','Opp','GS','W','L','SV','IP','BF','AB','H','2B','3B','HR','ER','BB','SO','HBP','SF']
    table = pf[pf[lg]==tm][pit_columns]
    if table.shape[0]==0:
        tbl_return = table[['Name','GS','Opp']]
    else:
        table.loc['Total'] = table.sum()
        table.loc[table.index[-1], 'Name'] = 'Total'
        table.loc[table.index[-1], 'H/A'] = '-'
        table.loc[table.index[-1], 'Opp'] = '-'
        table = rates_pit(table)
        x = table.loc[table.index[-1],'Inn']
        table.loc[table.index[-1],'IP'] = int((x-int(x))/.333)/10+int(x)
        tbl_return = table[['Name','H/A','Opp','GS','IP','H','ER','BB','HR','SO','avg','obp','slg','era','whip']].set_index('Name')
    return(tbl_return)

######

##########################################@
### Streamlit Page Build ###
###########################################

date = dt.datetime.today().strftime('%Y-%m-%d')
game_date = (dt.datetime.today()+dt.timedelta(days=-1))
display_date = f'{game_date:%A} {game_date:%b} {game_date.day}'
hit_num_cols = ['O','PA','AB','H','2B','3B','HR','R','RBI','SB','CS','BB','IBB','HBP','SO','SH','SF','GDP']
pit_num_cols = ['GS', 'W', 'L', 'SV', 'IP', 'H', 'R', 'ER', 'BB','SO', 'HR', 'HBP', 'GSc','AB','2B','3B','IBB','GDP','SF','SB','CS', 'PO','BF']

st.header("How did your players do yesterday?",divider = 'blue')

selected_league = st.selectbox(label='Select a DMB League',options = ['RJML','SSBL','CJPL'],index=0)

if selected_league == "RJML":
     my_team = "VAN"
elif selected_league == "SSBL":
     my_team = "NB"
elif selected_league =="CJPL":
     my_team = "OBS"


#get nice teams list for selectboxes
teams = keyID[keyID[selected_league].notna()][selected_league].unique().tolist()
teams.sort()
teams.remove('avail')
teams = teams+['Team Totals']


col1, col2 = st.columns([2,10])

with col1:
    selected_team = st.selectbox("Select a team",teams,index=teams.index(my_team))
    
    #if we want clear cache button...
    # st.write("To check for updates, click button at bottom of page, then reload browser.)")

    if selected_team == "Team Totals":
        team_hit_gl = rates(hf[[selected_league]+hit_num_cols].groupby(selected_league).sum())[['O','AB','H','2B','HR','R','RBI','BB','SO','SB','avg','obp','slg','ops']].sort_values(by=["ops",'O','HR','R'],ascending=False)
        team_pit_gl = rates_pit(pf[[selected_league]+pit_num_cols].groupby(selected_league).sum())[['GS','Inn','W','SV','H','ER','HR','BB','SO',,'avg','obp','slg','era','whip']].sort_values(by=["SO"],ascending=False)
        group = "Team"
    elif selected_team != "Team Totals":
        team_hit_gl = team_hit_log(lg=selected_league,tm=selected_team)
        team_pit_gl = team_pit_log(lg=selected_league,tm=selected_team)
        group = selected_team
        
with col2:
    tab1,tab2 = st.tabs(['Hitting','Pitching'])
    with tab1:
        st.subheader(group+' hitting, '+display_date)
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
        st.subheader(group+' pitching, '+display_date)
        st.dataframe(
            team_pit_gl,
            column_config={
                "avg": st.column_config.NumberColumn(format="%.3f"),
                "obp": st.column_config.NumberColumn(format="%.3f"),
                "slg": st.column_config.NumberColumn(format="%.3f"),
                "whip": st.column_config.NumberColumn(format="%.2f"),
                "era": st.column_config.NumberColumn(format="%.2f"),
                "Inn": st.column_config.NumberColumn(format="%.1f"),
            }
        )  

st.text("Data gathered from https://www.baseball-reference.com/leagues/daily.fcgi")

#if st.button("Clear cache"):
 #           st.cache_data.clear()