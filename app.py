import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")


### load tables
@st.cache_data
def load_key():
    return(pd.read_csv("https://mphitchman.com/DMB/csv/keyID.csv"))
keyID=load_key()

@st.cache_data
def load_hit():
    return(pd.read_csv("https://mphitchman.com/DMB/csv/hit24.csv"))
hit = load_hit()

@st.cache_data
def load_pit():
    return(pd.read_csv("https://mphitchman.com/DMB/csv/pit24.csv"))
pit = load_pit()
######


### player team total rate functions
def hit_rate_stats(df):
    '''df must have these columns: ['PA','AB','AB','H','2B','3B','HR','BB','SO','HBP','SF']'''
    df['avg'] = round(df['H']/df['AB'],3)
    df['obp'] = round((df['H']+df['BB']+df['HBP'])/(df['AB']+df['BB']+df['HBP']+df['SF']),3)
    df['slg'] = round((df['H']+df['2B']+2*df['3B']+3*df['HR'])/df['AB'],3)
    df['ops'] = df['obp']+df['slg']
    df['k%'] = round(df['SO']/df['PA']*100,1)
    df['bb%'] = round(df['BB']/df['PA']*100,1)
    df['babip'] = round((df['H']-df['HR'])/(df['AB']-df['HR']-df['SO']+df['SF']),3)
    df['k-bb%'] = df['k%']-df['bb%']
    return(df)

def pit_rate_stats(df):
    '''df must have these columns: ['Inn','TBF','AB','H','2B','3B','HR','ER','BB','SO','HBP','SF']'''
    import numpy as np
    #df['Inn'] = np.floor(df['IP'])+10*(df['IP']-np.floor(df['IP']))/3
    df['avg'] = round(df['H']/df['AB'],3)
    df['obp'] = round((df['H']+df['BB']+df['HBP'])/(df['AB']+df['BB']+df['HBP']+df['SF']),3)
    df['slg'] = round((df['H']+df['2B']+2*df['3B']+3*df['HR'])/df['AB'],3)
    df['ops'] = df['obp']+df['slg']
    df['k%'] = round(df['SO']/df['TBF']*100,1)
    df['bb%'] = round(df['BB']/df['TBF']*100,1)
    df['hr9'] = round(df['HR']/df['Inn']*9,1)
    df['whip'] = round((df['BB']+df['H'])/df['Inn'],2)
    df['era'] = round(df['ER']/df['Inn']*9,2)
    df['babip'] = round((df['H']-df['HR'])/(df['AB']-df['HR']-df['SO']+df['SF']),3)
    df['k-bb%'] = df['k%']-df['bb%']
    return(df)

def runs_created(df):
    '''df must have these columns: ['H','2B','3B','HR','BB','IBB','HBP','SF','SH','GDP','CS']'''
    #currently pit24 is missing 'SH'
    if 'SH' not in df.columns:
        df['SH'] = 0
    df['RC'] = round(((df['H']+df['BB']+df['HBP']-df['CS']-df['GDP'])*
                      (df['H']+df['2B']+2*df['3B']+3*df['HR']+
                       0.26*(df['BB']-df['IBB']+df['HBP'])+
                       0.52*(df['SH']+df['SF']+df['SB'])))/
                     (df['AB']+df['BB']+df['HBP']+df['SF']+df['SH']),3)
    df['RC27'] = round(df['RC']/(df['AB']-df['H']+df['GDP']+df['CS']+df['SF']+df['SH'])*27,2)
    return(df)

hit24 = hit_rate_stats(runs_created(hit))
pit24 = pit_rate_stats(runs_created(pit))
#####

### Aggregate functions and tables
@st.cache_data
def lg_team_totals(lgs=["RJML","SSBL"]):
    hit_count_stats = ['PA','AB','H','BB','HBP','IBB','SF','2B','3B','HR','R','RBI','SB','CS','SH','SO','GDP','O','WAR','Def','BsR','RC']
    pit_count_stats = ['G','GS','W','L','SV','Inn','TBF','AB','H','2B','3B','SF','ER','HR','BB','HBP','IBB','GDP','WP','BK','SO','SB','CS','WAR','RC']
    dfs = []
    for lg in lgs:
        tm_hit = hit_rate_stats(runs_created(hit24[[lg]+hit_count_stats].groupby(lg).sum()))
        tm_pit = pit_rate_stats(runs_created(pit24[[lg]+pit_count_stats].groupby(lg).sum()))
        tms = tm_hit.join(tm_pit, how='left',lsuffix='_h', rsuffix='_p').drop('avail').reset_index()
        tms = tms.rename(columns={lg:"Team"})
        tms = tms.rename(columns={tms.index.name:'Team'})
        tms['WAR_tot'] = tms['WAR_h']+tms['WAR_p']
        tms['xWpct'] = round(100*tms['RC27_h']**2/(tms['RC27_h']**2+tms['RC27_p']**2),1)
        tms['DMB'] = lg
        dfs.append(tms)
    tms = pd.concat(dfs)
    return(tms) 
  
tmtot = lg_team_totals()

teams = hit24['RJML'].unique().tolist()

def team_stats(lg="RJML",tm="VAN"):
    if tm not in hit24[lg].tolist():
        return(print(tm+" is not in the "+lg))
    else:
        bf = hit24[hit24[lg]==tm].set_index('Name')
        bf['Pos'] = bf['Pos'].fillna('')
        bf.loc['Team']= bf.sum()
        bf2 = hit_rate_stats(runs_created(bf))
        bf2.at['Team', 'xwOBA'] = weighted_avg(bf2.drop("Team"),"PA","xwOBA",3) #weighted xwOBA by players PA
        bf2.at['Team', 'Pos'] = '-'
        bf2[['PA','O','2B','3B','HR','R','RBI','SB','CS','BB','SO']] = bf2[['PA','O','2B','3B','HR','R','RBI','SB','CS','BB','SO']].astype(int)
        bf3 = bf2[['PA','2B','3B','HR','R','RBI','SB','BB','SO','Def','BsR','avg','obp','slg','ops','xwOBA','RC27','WAR','Pos']]
        
        pf = pit24[pit24[lg]==tm].set_index('Name')
        pf.loc['Team']= pf.sum()
        pf2 = pit_rate_stats(runs_created(pf))
        pf2[['G','GS','W','L','SV','TBF','H','ER','HR','BB','SO']] = pf2[['G','GS','W','L','SV','TBF','H','ER','HR','BB','SO']].astype(int)
        pf2['Inn'] = round(pf2['Inn'],1)
        pf2.at['Team', 'xFIP'] = weighted_avg(pf2.drop("Team"),"TBF","xFIP",2) #weighted xFIP by players TBF
        pf3 = pf2[['G','GS','W','L','SV','TBF','Inn','H','ER','HR','BB','SO','era','whip','k%','bb%','hr9','xFIP','RC27','WAR']]
        dfs = [bf3,pf3]
        return(dfs)
    
def weighted_avg(df,n="PA",x="xwOBA",rd=3):
    return(round(sum(df[n]*df[x])/sum(df[n]),rd))


######


##########################################@
### Streamlit Page Build ###
###########################################

teams = hit24['RJML'].unique().tolist()

st.title("MLB'24 Stats for RJML Teams")

tab1, tab2 = st.tabs(["Team","Team Comparison"])

with tab1:
    col1, col2, col3 = st.columns([1,5,5])

    with col1:
        selected_team = st.selectbox("Select a team",teams,index=teams.index("VAN"))

    if selected_team:
        hit_tm = team_stats(lg="RJML",tm=selected_team)[0]
        
        pit_tm = team_stats(lg="RJML",tm=selected_team)[1]
        
        with col2:
            st.header(selected_team+' Hitting')
            st.dataframe(hit_tm)
        with col3:
            st.header(selected_team+' Pitching')
            st.dataframe(pit_tm)


with tab2:
    col1,col2 = st.columns([6,6])
    with col1:
        df = lg_team_totals()
        tms = df[df['DMB']=="RJML"].set_index('Team')
        st.header('Team Snapshot')
        st.dataframe(tms[['PA','GS','RC27_h','RC27_p','ops_h','ops_p','WAR_h','WAR_p','xWpct']].sort_values(by='xWpct',ascending=False))
    with col2:
        x_var = 'RC27_h'
        y_var = 'RC27_p'
        fig = px.scatter(tmtot[tmtot['DMB']=='RJML'].reset_index(), x=x_var,y=y_var, hover_data=['Team','DMB'], color='xWpct',title="Team hit and pit RC27")
        fig.update_layout(showlegend=False)
        fig.update_traces(marker=dict(size=12,line=dict(width=2,color='DarkSlateGrey')),selector=dict(mode='markers'))
        st.plotly_chart(fig, use_container_width=True)
