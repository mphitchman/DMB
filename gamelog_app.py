import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from io import StringIO
import numpy as np
import re
import seaborn as sns
import warnings
warnings.simplefilter(action='ignore')
#warnings.simplefilter(action='ignore', category=FutureWarning)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px

st.set_page_config(layout="wide")

################
#### functions
################


## MLB average slash
@st.cache_data
def load_mlb_slash():
    url = "https://www.baseball-reference.com/leagues/majors/bat.shtml"
    page = requests.get(url)
    soup = bs(page.content)
    table = soup.select('table')[0]
    df = pd.read_html(StringIO(str(table)))[0]
    return([float(df['BA'][0]),float(df['OBP'][0]),float(df['SLG'][0])])
mlb_slash=load_mlb_slash()

def bbref_hit_gamelog(player_id):
    url = "https://www.baseball-reference.com/players/gl.fcgi?id="+player_id+"&t=b&year=2024"
    page = requests.get(url)
    soup = bs(page.content)
    player = soup.select('title')[0].string.split(' 2024')[0] # extracts player name
    table = soup.select('table')[4]
    gl = pd.read_html(StringIO(str(table)))[0]
    gl['Name'] = player
    gl = gl.drop(gl[gl.Date =="Date"].index)
    gl = gl.drop(['Unnamed: 5','aLI','WPA','Inngs','acLI','cWPA','RE24','DFS(DK)','DFS(FD)','ROE'], axis=1)
    gl = gl.replace(np.nan, 0)
    num_columns = ['Rk', 'Gcar', 'Gtm', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'IBB', 'SO', 'HBP', 'SH', 'SF', 'GDP', 'SB', 'CS', 'BA', 'OBP', 'SLG', 'OPS', 'BOP']
    gl[num_columns] = gl[num_columns].apply(pd.to_numeric,errors='coerce')
    gl = gl[:-1]
    gl['O'] = gl['H']+gl['2B']+2*gl['3B']+2*gl['HR']+gl['BB']+gl['SB']+gl['SH']+gl['R'] + gl['RBI']-gl['CS']-gl['GDP']
    # The following lines create a datetime column based on the string dates 
    # provided when data scraped. First we take care of dates like 'Apr 11 (n)' when
    #the game was (1) or (2) of a doublehader (requires re package)
    strings_to_replace = [' (1)', ' (2)']
    pattern = '|'.join(map(re.escape, strings_to_replace))
    gl['Date'] = gl['Date'].str.replace(pattern, '', regex=True)
    # now create new column of datetime objects
    date_format = "%b %d"
    gl['Date2'] = pd.to_datetime(gl['Date'], format=date_format)
    # Set a specific year for all dates
    gl['Date2'] = gl['Date2'].apply(lambda x: x.replace(year=2024))
    gl[['cum_PA', 'cum_AB', 'cum_H','cum_2B','cum_3B','cum_HR','cum_SO','cum_BB','cum_SF','cum_HBP','cum_O']] = gl[['PA', 'AB', 'H','2B','3B','HR','SO','BB','SF','HBP','O']].apply(lambda x: x.cumsum())
    return(gl)

def bat_slash(gl):
    df = pd.melt(gl[['Date2','avg','obp','slg','babip']], id_vars='Date2', value_vars=['avg','obp','slg','babip'])
    return(df)

def bat_contact(gl):
    df = pd.melt(gl[['Date2','bb%','k%']], id_vars = 'Date2', value_vars = ['bb%','k%'])
    return(df)

def cum_hit_rate_stats(df):
    '''df must have these columns: cum_PA,cum_AB,cum_AB,cum_H,cum_2B,cum_3B,cum_HR,cum_BB,cum_SO,cum_HBP,cum_SF'''
    df['avg'] = round(df['cum_H']/df['cum_AB'],3)
    df['obp'] = round((df['cum_H']+df['cum_BB']+df['cum_HBP'])/(df['cum_AB']+df['cum_BB']+df['cum_HBP']+df['cum_SF']),3)
    df['slg'] = round((df['cum_H']+df['cum_2B']+2*df['cum_3B']+3*df['cum_HR'])/df['cum_AB'],3)
    df['ops'] = df['obp']+df['slg']
    df['k%'] = round(df['cum_SO']/df['cum_PA']*100,1)
    df['bb%'] = round(df['cum_BB']/df['cum_PA']*100,1)
    df['babip'] = round((df['cum_H']-df['cum_HR'])/(df['cum_AB']-df['cum_HR']-df['cum_SO']+df['cum_SF']),3)
    return(df)

###### Pitchers

def IP_to_Inn(x):
    import numpy as np
    return(round(np.floor(x)+10*(x-np.floor(x))/3,5))

def cum_pit_rate_stats(df):
    '''df must have these columns: cum_(each of these: Inn,BF,AB,H,2B,3B,HR,ER,BB,SO,HBP,SF)'''
    df['avg'] = round(df['cum_H']/df['cum_AB'],3)
    df['obp'] = round((df['cum_H']+df['cum_BB']+df['cum_HBP'])/(df['cum_AB']+df['cum_BB']+df['cum_HBP']+df['cum_SF']),3)
    df['slg'] = round((df['cum_H']+df['cum_2B']+2*df['cum_3B']+3*df['cum_HR'])/df['cum_AB'],3)
    df['ops'] = df['obp']+df['slg']
    df['k%'] = round(df['cum_SO']/df['cum_BF']*100,1)
    df['bb%'] = round(df['cum_BB']/df['cum_BF']*100,1)
    df['hr9'] = round(df['cum_HR']/df['cum_Inn']*9,1)
    df['whip'] = round((df['cum_BB']+df['cum_H'])/df['cum_Inn'],2)
    df['era'] = round(df['cum_ER']/df['cum_Inn']*9,2)
    df['babip'] = round((df['cum_H']-df['cum_HR'])/(df['cum_AB']-df['cum_HR']-df['cum_SO']+df['cum_SF']),3)
    return(df)

def bbref_pit_gamelog(player_id):
    url = "https://www.baseball-reference.com/players/gl.fcgi?id="+player_id+"&t=p&year=2024"
    page = requests.get(url)
    soup = bs(page.content)
    player = soup.select('title')[0].string.split(' 2024')[0] # extracts player name
    table = soup.select('table')[0]
    gl = pd.read_html(StringIO(str(table)))[0]
    gl['Name'] = player
    gl = gl.drop(gl[gl.Opp =="Opp"].index)
    gl = gl.drop(['Unnamed: 5','aLI','WPA','Inngs','acLI','cWPA','RE24','DFS(DK)','DFS(FD)','ROE','Entered','Exited'], axis=1)
    gl = gl.replace(np.nan, 0)
    num_columns = ['Rk', 'Gcar', 'Gtm', 'IP','AB', 'BF', 'ER', 'H', '2B', '3B', 'HR', 'BB', 'IBB', 'SO', 'HBP', 'SF', 'GDP', 'SB', 'CS','ERA','FIP','Pit','Str']
    gl[num_columns] = gl[num_columns].apply(pd.to_numeric,errors='coerce')
    gl = gl[:-1]
    strings_to_replace = [' (1)', ' (2)','(1)','(2)']
    pattern = '|'.join(map(re.escape, strings_to_replace))
    gl['Date'] = gl['Date'].str.replace(pattern, '', regex=True)
    # now create new column of datetime objects
    date_format = "%b %d"
    gl['Date2'] = pd.to_datetime(gl['Date'], format=date_format)
    # Set a specific year for all dates
    gl['Date2'] = gl['Date2'].apply(lambda x: x.replace(year=2024))
    gl['Inn'] = gl['IP'].apply(IP_to_Inn)
    gl[['cum_Inn', 'cum_BF', 'cum_AB', 'cum_H','cum_2B','cum_3B','cum_HR','cum_SO','cum_BB','cum_SF','cum_HBP','cum_ER']] = gl[['Inn', 'BF','AB', 'H','2B','3B','HR','SO','BB','SF','HBP','ER']].apply(lambda x: x.cumsum())
    return(gl)

def pit_slash(gl):
    df = pd.melt(gl[['Date2','avg','obp','slg']], id_vars='Date2', value_vars=['avg','obp','slg'])
    return(df)

def pit_contact(gl):
    df = pd.melt(gl[['Date2','bb%','k%']], id_vars = 'Date2', value_vars = ['bb%','k%'])
    return(df)

##################
#### data scrape
##################


key_van_hit = ['arciaor01', 'castrwi01', 'rileyau01', 'larnatr01', 'isbelky01', 'bensowi01', 'marshbr02', 
               'morenga01', 'sosale01', 'roberlu01', 'carroco02', 'pasquvi01', 'goodmhu01']

key_nb_hit = ['martijd02', 'altuvjo01', 'troutmi01', 'belljo02', 'seageco01', 'delacbr01',  
              'rengilu01', 'melenmj01', 'paredis01', 'ohopplo01', 'hendegu01']


def load_team_hitters(idx,team="VAN"):
    dfs = []
    for key in idx:
        df = cum_hit_rate_stats(bbref_hit_gamelog(key))
        dfs.append(df)
    hitgl = pd.concat(dfs, ignore_index=True)
    hitgl['DMB'] = team
    return(hitgl)

@st.cache_data
def load_hit():
    van=load_team_hitters(key_van_hit,team="VAN")
    nb = load_team_hitters(key_nb_hit,team="NB")
    return(pd.concat([van,nb],ignore_index=True))
hit_gl = load_hit()

name_van_hit = hit_gl[hit_gl['DMB']=="VAN"].sort_values(by="cum_O",ascending=False)['Name'].unique()
name_nb_hit = hit_gl[hit_gl['DMB']=="NB"].sort_values(by="cum_O",ascending=False)['Name'].unique()

def positions_played(name,min=2):
    '''extracts positions played (a min of 'min' games) from bbref gamelogs scrape'''
    x = hit_gl[hit_gl['Name']==name]['Pos'].tolist() # a list of positions played, one element per day, so includes entries like 'PH LF'
    pos_played = [pos for pos_day in x for pos in pos_day.split()] #this splits each entry by spaces and creates new list
    pos = ['C','1B','2B','3B','SS','LF','CF','RF','DH']
    pos_count = []
    for p in pos:
        pos_count.append(sum(p == s for s in pos_played))
    df = pd.DataFrame({'pos':pos, 'games':pos_count}).sort_values(by='games',ascending=False)
    return(','.join(df[df['games']>=min]['pos'].tolist()))

def hit_roll_rates(df_input=hit_gl,name = "Vinnie Pasquantino",n = 15):
    df_name = df_input[df_input['Name']==name][['Date2','Name']]
    df = df_input[df_input['Name']==name][['PA','AB','H','2B','3B','HR','R','RBI','SB','CS','BB','SO','HBP','SF','SH','IBB','O']].rolling(n).sum()
    df['avg'] = round(df['H']/df['AB'],3)
    df['obp'] = round((df['H']+df['BB']+df['HBP'])/(df['AB']+df['BB']+df['HBP']+df['SF']),3)
    df['slg'] = round((df['H']+df['2B']+2*df['3B']+3*df['HR'])/df['AB'],3)
    df['ops'] = df['obp']+df['slg']
    df['k%'] = round(df['SO']/df['PA']*100,1)
    df['bb%'] = round(df['BB']/df['PA']*100,1)
    df = pd.concat([df_name,df],axis=1)
    return(df)


##########################################@
### Streamlit Page Build ###
###########################################

st.title("MLB'24 Game Logs for my guys")

tab1, tab2, tab3 = st.tabs(["hitters","pitchers","O Race"])

with tab1:
    col1, col2, col3 = st.columns([2,6,4])

    with col1:
        names = name_van_hit.tolist()+name_nb_hit.tolist()
        selected_hitter = st.selectbox("Select a hitter",names)

    if selected_hitter:
        with col2:
            st.header(selected_hitter)
            df = hit_gl[hit_gl['Name']==selected_hitter].sort_values(by="Date2",ascending=False)[['Rk','Date','PA','O','H','2B','HR','R','RBI','SB','BB','SO','avg','obp','slg','ops','bb%','k%']]
            st.dataframe(df)
        with col3:
            k=15 #rolling average number of days
            df = hit_roll_rates(hit_gl,selected_hitter,n=k)
            fig, ax = plt.subplots()
            sns.lineplot(data = df[['Date2','avg','obp','slg']].set_index('Date2'), ax=ax).set_title(selected_hitter+' '+str(k)+'-day rolling rates')
            ax.hlines(y = mlb_slash,xmin=hit_gl['Date2'].min(),xmax=df['Date2'].max(),linestyles="dashed",colors=['blue','orange','green'])
            locator = mdates.MonthLocator(bymonth=[4,5,6])
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
            st.pyplot(fig)
            
with tab2:

    st.header("TODO")

with tab3:

    st.header("2024 O Race")
    fig = px.line(hit_gl, x="Date2", y="cum_O", color='Name',width=1000, height=600)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)
