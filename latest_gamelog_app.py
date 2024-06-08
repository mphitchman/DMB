import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from io import StringIO

st.set_page_config(layout="wide")

st.title("Yesterday's Player Game Logs")

# functions used
def flatten(xss):
    return [x for xs in xss for x in xs]

@st.cache_data
def hit_rate_stats(df):
    df['avg'] = round(df['H']/df['AB'],3)
    df['obp'] = round((df['H']+df['BB']+df['HBP'])/(df['AB']+df['BB']+df['HBP']+df['SF']),3)
    df['slg'] = round((df['H']+df['2B']+2*df['3B']+3*df['HR'])/df['AB'],3)
    df['ops'] = df['obp']+df['slg']
    df['K%'] = round(df['SO']/df['PA']*100,1)
    df['BB%'] = round(df['BB']/df['PA']*100,1)
    df['BABIP'] = round((df['H']-df['HR'])/(df['AB']-df['HR']-df['SO']+df['SF']),3)
    return(df)

def add_O(df,pct=False):
    df['O'] = df['H']+df['2B']+2*df['3B']+2*df['HR']+df['BB']+df['SB']+df['SH']+df['R'] + df['RBI']-df['CS']-df['GDP']
    if pct==True:
        df['O%'] = round(df['O']/df['PA']*100,1)
    return(df)

@st.cache_data
def IP_to_Inn(x):
    import numpy as np
    return(round(np.floor(x)+10*(x-np.floor(x))/3,5))

@st.cache_data
def pit_rate_stats(df):
    '''df must have these columns: ['IP','BF','AB','H','2B','3B','HR','ER','BB','SO','HBP','SF']'''
    import numpy as np
    df['Inn'] = np.floor(df['IP'])+10*(df['IP']-np.floor(df['IP']))/3
    df['avg'] = round(df['H']/df['AB'],3)
    df['obp'] = round((df['H']+df['BB']+df['HBP'])/(df['AB']+df['BB']+df['HBP']+df['SF']),3)
    df['slg'] = round((df['H']+df['2B']+2*df['3B']+3*df['HR'])/df['AB'],3)
    df['ops'] = df['obp']+df['slg']
    df['K%'] = round(df['SO']/df['BF']*100,1)
    df['BB%'] = round(df['BB']/df['BF']*100,1)
    df['HR9'] = round(df['HR']/df['Inn']*9,1)
    df['WHIP'] = round((df['BB']+df['H'])/df['Inn'],2)
    df['ERA'] = round(df['ER']/df['Inn']*9,2)
    df['BABIP'] = round((df['H']-df['HR'])/(df['AB']-df['HR']-df['SO']+df['SF']),3)
    return(df)

# load data
# keyID
@st.cache_data
def load_key():
    return(pd.read_csv("https://mphitchman.com/DMB/keyID.csv"))
keyID=load_key()

#yesterday's hitting game logs
@st.cache_data
def load_hitgl():
    url = "https://www.baseball-reference.com/leagues/daily.fcgi?request=1&type=b&dates=yesterday&lastndays&lastndays=7&since=2024-06-01&fromandto=2024-06-01.2024-06-30&level=mlb&franch=ANY"
    page = requests.get(url)
    soup = bs(page.content)
    table = soup.select('table')[0] 
    t = table.find_all('a')
    urls = [tag['href'] for tag in t]
    cont = [tag.contents for tag in t]
    cont = flatten(cont)
    mlbid=[]
    names=[]
    for i in range(len(urls)):
        if 'mlb_ID' in urls[i]:
            mlbid.append(eval(urls[i].replace('/redirect.fcgi?player=1&mlb_ID=', '')))
            names.append(cont[i])
    bbref_key = pd.DataFrame({'Name':names,'key_MLB':mlbid})
    gl = pd.read_html(StringIO(str(table)))[0][['Name','Age','Tm','PA','AB','R','H','2B','3B', 'HR','RBI','BB','IBB','SO','HBP','SH','SF','GDP','SB','CS']]
    gl = gl.drop(gl[gl.Age =="Age"].index)
    hit_gly = gl.merge(bbref_key,on="Name",how='left')
    num_columns = ['Age', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'IBB', 'SO', 'HBP', 'SH', 'SF', 'GDP', 'SB', 'CS']
    hit_gly[num_columns] = hit_gly[num_columns].apply(pd.to_numeric)
    hit_gly = hit_gly.merge(keyID[['key_MLB','RJML','SSBL','CJPL']])
    return(hit_gly)
  
hit_gl = load_hitgl()

#yesterday's pitching game logs
@st.cache_data
def load_pitgl():
    url = "https://www.baseball-reference.com/leagues/daily.fcgi?request=1&type=p&dates=yesterday&lastndays=7&since=2024-06-01&fromandto=2024-06-01.2024-06-30&level=mlb&franch=ANY"
    page = requests.get(url)
    soup = bs(page.content)
    table = soup.select('table')[0] 
    t = table.find_all('a')
    urls = [tag['href'] for tag in t]
    cont = [tag.contents for tag in t]
    cont = flatten(cont)
    mlbid=[]
    names=[]
    for i in range(len(urls)):
        if 'mlb_ID' in urls[i]:
            mlbid.append(eval(urls[i].replace('/redirect.fcgi?player=1&mlb_ID=', '')))
            names.append(cont[i])
    bbref_key = pd.DataFrame({'Name':names,'key_MLB':mlbid})
    gl = pd.read_html(StringIO(str(table)))[0][['Name', 'Age', 'Tm', 'GS', 'W', 'L', 'SV', 'IP', 'BF', 'H', 'R', 'ER', 'BB', 'SO', 'HR', 'HBP', 'AB', '2B', '3B', 'IBB', 'GDP', 'SF', 'SB', 'CS']]
    gl = gl.drop(gl[gl.Age =="Age"].index)
    pit_gly = gl.merge(bbref_key,on="Name",how='left')
    num_columns = ['Age', 'GS', 'W', 'L', 'SV', 'IP', 'BF', 'H', 'R', 'ER', 'BB', 'SO', 'HR', 'HBP', 'AB', '2B', '3B', 'IBB', 'GDP', 'SF', 'SB', 'CS']
    pit_gly[num_columns] = pit_gly[num_columns].apply(pd.to_numeric)
    pit_gly = pit_gly.merge(keyID[['key_MLB','RJML','SSBL','CJPL']])
    return(pit_gly) 


pit_gl = load_pitgl()




teams = list(keyID.RJML.unique())
teams.append("NB")
teams.sort()



col1, col2, col3 = st.columns([1,5,5])

with col1:
    selected_team = st.selectbox("Select a team",teams,index=teams.index("VAN"))


if selected_team!="NB":
    hit_tm = hit_gl[hit_gl.RJML==selected_team].set_index('Name')
    hit_tm.loc['Team']=hit_tm.sum()
    hit_tm = hit_rate_stats(hit_tm).sort_values(by="O",ascending=False)[['PA','AB','H','2B','3B','HR','RBI','R','SB','BB','SO','avg','obp','slg','O']]
    pit_tm = pit_gl[pit_gl.RJML==selected_team].sort_values(by=['IP','SO'],ascending=False).set_index('Name')
    pit_tm.loc['Team']=pit_tm.sum()
    pit_tm = pit_rate_stats(pit_tm)[['Name','GS','IP','H','ER','HR','SO','BB','BF','W','L','SV','ERA','WHIP']]
    
    with col2:
        st.header(selected_team+' Hitting')
        st.dataframe(hit_tm)
    with col3:
        st.header(selected_team+' Pitching')
        st.dataframe(pit_tm)

if selected_team=="NB":
    hit_tm = hit_gl[hit_gl.SSBL==selected_team].set_index('Name')
    hit_tm.loc['Team']=hit_tm.sum()
    hit_tm = hit_rate_stats(hit_tm).sort_values(by="O",ascending=False)[['PA','AB','H','2B','3B','HR','RBI','R','SB','BB','SO','avg','obp','slg','O']]
    pit_tm = pit_gl[pit_gl.SSBL==selected_team].sort_values(by=['IP','SO'],ascending=False).set_index('Name')
    pit_tm.loc['Team']=pit_tm.sum()
    pit_tm = pit_rate_stats(pit_tm)[['Name','GS','IP','H','ER','HR','SO','BB','BF','W','L','SV','ERA','WHIP']]
    
    with col2:
        st.header(selected_team+' Hitting')
        st.dataframe(hit_tm)
    with col3:
        st.header(selected_team+' Pitching')
        st.dataframe(pit_tm)
