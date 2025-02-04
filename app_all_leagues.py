import streamlit as st
import pandas as pd
import numpy as np
import os.path, time
import plotly.express as px

st.set_page_config(layout="wide")


### load tables
@st.cache_data
def load_hit():
    return(pd.read_csv("https://mphitchman.com/DMB/csv/hit24_summary.csv"))
hit = load_hit()
hit['Pos'] = hit['Pos'].replace(",","",regex=True)

@st.cache_data
def load_pit():
    return(pd.read_csv("https://mphitchman.com/DMB/csv/pit24_summary.csv"))
pit = load_pit()

### team total rate functions

def hit_rate_stats(df):
    # df must have these columns: ['PA','AB','AB','H','2B','3B','HR','BB','K','HBP','SF']
    df['AVG'] = round(df['H']/df['AB'],3)
    df['OBP'] = round((df['H']+df['BB']+df['HBP'])/(df['AB']+df['BB']+df['HBP']+df['SF']),3)
    df['SLG'] = round((df['H']+df['2B']+2*df['3B']+3*df['HR'])/df['AB'],3)
    df['OPS'] = df['OBP']+df['SLG']
    df['k%'] = round(df['K']/df['PA']*100,1)
    df['bb%'] = round(df['BB']/df['PA']*100,1)
    df['BABIP'] = round((df['H']-df['HR'])/(df['AB']-df['HR']-df['K']+df['SF']),3)
    df['k-bb%'] = df['k%']-df['bb%']
    return(df)

def pit_rate_stats(df):
    # df must have these columns: ['Inn','TBF','AB','H','2B','3B','HR','ER','BB','K','HBP','SF']
    df['AVG'] = round(df['H']/df['AB'],3)
    df['OBP'] = round((df['H']+df['BB']+df['HBP'])/(df['AB']+df['BB']+df['HBP']+df['SF']),3)
    df['SLG'] = round((df['H']+df['2B']+2*df['3B']+3*df['HR'])/df['AB'],3)
    df['OPS'] = df['OBP']+df['SLG']
    df['k%'] = round(df['K']/df['TBF']*100,1)
    df['bb%'] = round(df['BB']/df['TBF']*100,1)
    df['gb%'] = round(df['GB']/df['battedballs']*100,1)
    df['hr9'] = round(df['HR']/df['Inn']*9,1)
    df['WHIP'] = round((df['BB']+df['H'])/df['Inn'],2)
    df['ERA'] = round(df['ER']/df['Inn']*9,2)
    df['BABIP'] = round((df['H']-df['HR'])/(df['AB']-df['HR']-df['K']+df['SF']),3)
    df['k-bb%'] = df['k%']-df['bb%']
    return(df)

def runs_created(df):
    #df must have these columns: ['H','2B','3B','HR','BB','IBB','HBP','SF','SH','GDP','CS']
    if 'SH' not in df.columns:
        df['SH'] = 0
    df['RC'] = round(((df['H']+df['BB']+df['HBP']-df['CS']-df['GDP'])*
                      (df['H']+df['2B']+2*df['3B']+3*df['HR']+
                       0.26*(df['BB']-df['IBB']+df['HBP'])+
                       0.52*(df['SH']+df['SF']+df['SB'])))/
                     (df['AB']+df['BB']+df['HBP']+df['SF']+df['SH']),3)
    df['RC27'] = round(df['RC']/(df['AB']-df['H']+df['GDP']+df['CS']+df['SF']+df['SH'])*27,2)
    return(df)

#amend tables
hit24 = hit_rate_stats(runs_created(hit))
pit24 = pit_rate_stats(runs_created(pit))
hit24['XBH']=hit24['2B']+hit24['3B']+hit24['HR']

#counting stats considered
hit_count_stats = ['PA','AB','H','BB','HBP','IBB','SF','2B','3B','HR','R','RBI','SB','CS','SH','K','GDP','O','WAR','Def','BsR','RC']
pit_count_stats = ['G','GS','W','L','SV','Inn','TBF','AB','H','2B','3B','SF','ER','HR','BB','HBP','IBB','GDP','K','SB','CS','WAR','RC','GB','battedballs']


#####

### Aggregate functions 
def weighted_avg(df,n="PA",x="XWOBA",rd=3):
    return(round(sum(df[n]*df[x])/sum(df[n]),rd))

def team_stats(lg="RJML",tm="VAN"):
    bf = hit24[hit24[lg]==tm].set_index('Name')
    bf.loc['Team']= bf.sum()
    bf2 = hit_rate_stats(runs_created(bf))
    bf2.at['Team', 'XWOBA'] = weighted_avg(bf2.drop("Team"),"PA","XWOBA",3) #weighted xwOBA by players PA
    bf2.at['Team','opsL'] = weighted_avg(bf2.drop("Team"),"PAL","opsL",3)
    bf2.at['Team','opsR'] = weighted_avg(bf2.drop("Team"),"PAR","opsR",3)
    bf2.at['Team', 'Pos'] = '-'
    bf2[['PA','O','2B','3B','HR','R','RBI','SB','CS','BB','K','XBH']] = bf2[['PA','O','2B','3B','HR','R','RBI','SB','CS','BB','K','XBH']].astype(int)
    bf3 = bf2[['PA','opsL','opsR','XBH','HR','R','RBI','SB','BB','K','AVG','OBP','SLG','OPS','XWOBA','RC27','WAR','Pos']]
        
    pf = pit24[pit24[lg]==tm].set_index('Name')
    pf.loc['Team']= pf.sum()
    pf2 = pit_rate_stats(runs_created(pf))
    pf2[['G','GS','W','L','SV','TBF','H','ER','HR','BB','K']] = pf2[['G','GS','W','L','SV','TBF','H','ER','HR','BB','K']].astype(int)
    pf2['Inn'] = round(pf2['Inn'],1)
    pf2.at['Team', 'xFIP'] = weighted_avg(pf2.drop("Team"),"TBF","xFIP",2) #weighted xFIP by players TBF
    pf2.at['Team','opsL'] = weighted_avg(pf2.drop("Team"),"TBFL","opsL",3)
    pf2.at['Team','opsR'] = weighted_avg(pf2.drop("Team"),"TBFR","opsR",3)
    pf3 = pf2[['G','GS','opsL','opsR','W','L','SV','TBF','H','ER','HR','BB','K','ERA','WHIP','k%','bb%','hr9','gb%','xFIP','RC27','WAR','k-bb%']]
    dfs = [bf3,pf3]
    return(dfs)

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
teams = hit24[hit24[selected_league].notna()][selected_league].unique().tolist()
teams.sort()
#teams.remove('avail')
teams = teams+['Team Totals']

col1, col2 = st.columns([2,10])

with col1:
    selected_team = st.selectbox("Select a team",teams,index=teams.index(my_team))
    st.write("Last update: 29-Nov-24")
    #if we want clear cache button...
    # st.write("To check for updates, click button at bottom of page, then reload browser.)")

    if selected_team == "Team Totals":
        hit_tm = hit_rate_stats(runs_created(hit24[[selected_league]+hit_count_stats].groupby(selected_league).sum()))
        pit_tm = pit_rate_stats(runs_created(pit24[[selected_league]+pit_count_stats].groupby(selected_league).sum()))
        
    elif selected_team != "Team Totals":
        hit_tm = team_stats(lg=selected_league,tm=selected_team)[0]
        
        pit_tm = team_stats(lg=selected_league,tm=selected_team)[1]
        
with col2:
    tab1,tab2,tab3 = st.tabs(['Hitting','Pitching','Plots'])
    with tab1:
        st.header(selected_team+' - Hitting')
        st.dataframe(
            hit_tm,
            column_config={
                "AVG": st.column_config.NumberColumn(format="%.3f"),
                "OBP": st.column_config.NumberColumn(format="%.3f"),
                "SLG": st.column_config.NumberColumn(format="%.3f"),
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
            pit_tm,
            column_config={
                "ERA": st.column_config.NumberColumn(format="%.2f"),
                "xFIP": st.column_config.NumberColumn(format="%.2f"),
                "WHIP": st.column_config.NumberColumn(format="%.2f"),
                "WAR": st.column_config.NumberColumn(format="%.1f"),
                "RC27": st.column_config.NumberColumn(format="%.1f"),
                "hr9": st.column_config.NumberColumn(format="%.1f"),
                "bb%": st.column_config.NumberColumn(format="%.1f"),
                "k%": st.column_config.NumberColumn(format="%.1f"),
                "gb%": st.column_config.NumberColumn(format="%.1f"),
                "Inn": st.column_config.NumberColumn(format="%.1f"),
            }
        )
    
    with tab3:
        #find mlb avgs (estimate in the case of xwoba)
        mph = hit24[['PA','AB','H','BB','HBP','IBB','SF','2B','3B','HR','R','RBI','SB','CS','SH','K','GDP','O','WAR','Def','BsR','RC','XWOBA']].copy()
        mph.loc['Total',:]=mph.sum()
        lg_avg = hit_rate_stats(runs_created(mph))
        lg_avg.at['Total', 'XWOBA'] = weighted_avg(lg_avg.drop("Total"),"PA","XWOBA",3)
        lg_ops = lg_avg.at['Total','OPS']
        lg_kbb = lg_avg.at['Total','k-bb%']
        lg_xwoba = lg_avg.at['Total','XWOBA']
        lg_rc27 = lg_avg.at['Total','RC27'] 
        colA,colB = st.columns([5,5])

        if selected_team=="Team Totals":
             hovname = selected_league
        if selected_team!="Team Totals":
             hovname ='Name'
        
        
        with colA:
             hit_tm['Team']=hit_tm.index=='Team'
             fig = px.scatter(hit_tm.reset_index(), x='OPS',y='RC27',color='Team',
                              hover_name = hovname,
                              hover_data = {'Team':False, # remove Team from hover data
                                            'OPS':':.3f',
                                            'RC27':':.1f',
                                            'PA': True},
                                            title=selected_team+" Hitting OPS and RC27")
             fig.add_vline(x=lg_ops, line_width=1, line_dash='dash', line_color='red',annotation_text='mlb avg')
             fig.add_hline(y=lg_rc27, line_width=1, line_dash='dash', line_color='red',annotation_text='mlb avg')
             fig.update_traces(marker=dict(size=10,line=dict(width=2,color='DarkSlateGrey')),selector=dict(mode='markers'),
                               #hovertemplate='%{hovname}<br>Número de ingressantes=%{y}'
                               )
             fig.update_layout(showlegend=False)
             st.plotly_chart(fig, use_container_width=True) 
        with colB:
             pit_tm['Team']=pit_tm.index=='Team'
             fig = px.scatter(pit_tm.reset_index(), y='RC27',x='k-bb%',color='Team',
                              hover_name = hovname,
                              hover_data = {'Team':False, # remove Team from hover data
                                            'k-bb%':':.1f',
                                            'RC27':':.1f',
                                            'TBF': True},
                                            title=selected_team+" Pitching RC27 and k-bb%")
             fig.add_vline(x=lg_kbb, line_width=1, line_dash='dash', line_color='red',annotation_text='mlb avg')
             fig.add_hline(y=lg_rc27, line_width=1, line_dash='dash', line_color='red',annotation_text='mlb avg')
             fig.update_layout(showlegend=False)
             fig.update_traces(marker=dict(size=10,line=dict(width=2,color='DarkSlateGrey')),selector=dict(mode='markers'))
             st.plotly_chart(fig, use_container_width=True)   

#if st.button("Clear cache"):
 #           st.cache_data.clear()
