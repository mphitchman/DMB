import streamlit as st
import pandas as pd
import pybaseball as pyb

st.set_page_config(layout="wide")

st.title("MLB'24 Stats for RJML Teams")

# load data
@st.cache_data
def load_key():
    return(pd.read_csv("https://mphitchman.com/DMB/keyID.csv"))
mph=load_key()

@st.cache_data
def load_hit():
    df = pyb.fg_batting_data(start_season=2024,qual=10)
    df = df.rename(columns={"IDfg": "key_FG","Team":"MLB"})
    df = df.merge(mph[mph['type']=="B"][['type','key_FG','RJML']],on="key_FG",how='left').set_index('Name')
    return(df)
hit24 = load_hit()

@st.cache_data
def load_pitbref():
    pf = pyb.pitching_stats_bref()
    pf = pf.rename(columns={"mlbID": "key_MLB","Name": "Name_bbref"})
    pf["key_MLB"] = pd.to_numeric(pf["key_MLB"])
    return(pf[['IP','BF','AB','H','2B','3B','HR','ER','BB','SO','HBP','SF','key_MLB']])

@st.cache_data
def load_pit():
    pf = pyb.pitching_stats_bref()
    pf = pf.rename(columns={"mlbID": "key_MLB"})
    pf["key_MLB"] = pd.to_numeric(pf["key_MLB"])
    df = pyb.fg_pitching_data(start_season=2024,qual=10)
    df = df.rename(columns={"IDfg": "key_FG","Team":"MLB"})
    df = df.merge(mph[mph['type']=="P"][['type','key_FG','key_MLB','RJML']],on="key_FG",how='left')
    df = df.merge(pf[['BF','AB','2B','3B','SF','key_MLB']],on='key_MLB',how='left')
    return(df.set_index('Name'))
pit24 = load_pit()

# rate stat functions
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

def team_pit_totals(df):
    pit_count_stats = ['RJML','GS','IP','BF','AB','H','2B','3B','HR','BB','HBP','SF','IBB','SO','ER','W','L','SV']
    return(pit_rate_stats(df[pit_count_stats].groupby('RJML').sum()))

def team_hit_totals(df):
    hit_count_stats = ['RJML','G','PA','AB','H','2B','3B','HR','BB','HBP','SF','IBB','SO','R','RBI','SB','CS','SH','GDP']
    return(hit_rate_stats(df[hit_count_stats].groupby('RJML').sum()))

hit_summary_columns = ['PA','H','2B','3B','HR','R','RBI','avg','obp','slg','ops','BB%','K%','BABIP']
pit_summary_columns = ['GS','W','L','SV','ERA','WHIP','avg','obp','slg','ops','BB%','K%','HR9','BABIP']

teams = ['League','ALA', 'BRA', 'CAM', 'CC', 'CK', 'DAY', 'DV', 'GH', 'GNB', 'GRF', 'HAL', 'HAR', 
          'HIG', 'HOM', 'PR', 'RAC', 'RAM', 'RM', 'ROC', 'STE', 'SV', 'TB', 'VAN', 'WHI']

col1, col2, col3 = st.columns([1,5,5])

with col1:
    selected_team = st.selectbox("Select a team",teams[0:25],index=teams.index("VAN"))

if selected_team == "League":
    hit_tm = team_hit_totals(hit24)[hit_summary_columns]
    pit_tm = team_pit_totals(pit24)[pit_summary_columns]
    with col2:
        st.header('Team Hitting')
        st.dataframe(hit_tm)
    with col3:
        st.header('Team Pitching')
        st.dataframe(pit_tm)
    
        
if selected_team != "RJML":
    if selected_team=="NB":
        hit_tm = hit24[hit24.SSBL==selected_team]
        pit_tm = pit24[pit24.SSBL==selected_team]
    else:
        hit_tm = hit24[hit24.RJML==selected_team]
        pit_tm = pit24[pit24.RJML==selected_team]
    
    hit_tm.loc['total']=hit_tm.sum()
    hit_tm = hit_rate_stats(hit_tm)
    hit_tm['MLB'][-1]="--"
    hit_tm['Age'][-1]=round(hit_tm['Age'][0:-1].mean(),1)
    hit_tm['wRC+'][-1]=round(sum(hit_tm[0:-1]['PA']*hit_tm[0:-1]['wRC+'])/sum(hit_tm[0:-1]['PA']),0)
    hit_tm = hit_tm[['PA','ops','wRC+','WAR','avg','obp','slg','BB%','K%','BABIP','2B','3B','HR','R','RBI','Off','Fld','BsR','MLB','Age']]
    
    pit_tm.loc['total']=pit_tm.sum()
    pit_tm = pit_rate_stats(pit_tm)
    pit_tm['GB%']=round(pit_tm['GB%']*100,1)
    pit_tm['MLB'][-1]="--"
    pit_tm['GB%'][-1]="--"
    pit_tm['Age'][-1]=round(pit_tm['Age'][0:-1].mean(),1)
    pit_tm['xFIP'][-1]=round(sum(pit_tm[0:-1]['TBF']*pit_tm[0:-1]['xFIP'])/sum(pit_tm[0:-1]['TBF']),2)
    pit_tm['CSW%'][-1]=round(sum(pit_tm[0:-1]['TBF']*pit_tm[0:-1]['CSW%'])/sum(pit_tm[0:-1]['TBF']),3)
    pit_tm['Inn'] = round(pit_tm['Inn'],1)
    pit_tm = pit_tm[['GS','ops','ERA','WHIP','WAR','BF','BB%','K%','HR9','avg','obp','slg','GB%','BABIP','xFIP','MLB','Age']]
    
    with col2:
        st.header(selected_team+' Hitting')
        st.dataframe(hit_tm)
    with col3:
        st.header(selected_team+' Pitching')
        st.dataframe(pit_tm)
