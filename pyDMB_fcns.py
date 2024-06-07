#player key_ID lookup
def player_key(name,org):
    ''' return key_org, for player 'name', where org is MLB, FG, or bbref'''
    import pandas as pd
    key = pd.read_csv("csv/keyID.csv")
    return(key[key['Name']==name][["key_"+org]].iloc[0,0])


#add dmb teams to data frame with keyID:

def add_DMB(df,type="B",key="key_MLB",leagues = ['RJML','SSBL','CJPL']):
    ''' add team affiliations in DMB league(s) to a data frame containing type ("B" or "P") of player, by certain player key''' 
    import pandas as pd
    keyID = pd.read_csv("csv/keyID.csv")
    df = df.merge(keyID[keyID['type']==type][['type','key_MLB','key_FG','key_bbref']+leagues],on=key,how='left')
    return(df)




#pitching functions

def IP_to_Inn(x):
    import numpy as np
    return(round(np.floor(x)+10*(x-np.floor(x))/3,5))

def pit_rate_stats(df):
    '''df must have these columns: Inn,BF,AB,H,2B,3B,HR,ER,BB,SO,HBP,SF'''
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

def team_pit_display(tm,lg,qual=1):
    ''' prints pitchers for team in a league having at least qual IP, along with team totals for these qualified pitchers'''
    pit_count_stats = ['G','GS','W','L','SV','Inn','BF','AB','H','2B','3B','HR','BB','HBP','SF','IBB','SO','ER']
    pp = pit[(pit[lg]==tm)&(pit['Inn']>=qual)][['Name']+pit_count_stats].sort_values('Inn',ascending=False).fillna(0)
    pp.loc['Team']= pp.sum()
    pp['Inn'] = round(pp['Inn'],1)
    pp.iloc[-1,0]="Team"
    pp = pit_rate_stats(pp)
    pit_summary_columns = ['G','GS','W','L','SV','BF','Inn','H','SO','BB','avg','obp','slg','ops','K%','BB%','HR9','WHIP','ERA']

    return(pp[['Name']+pit_summary_columns]) 



#hitting functions

def add_O(df):
    df['O'] = df['H']+df['2B']+2*df['3B']+2*df['HR']+df['BB']+df['SB']+df['SH']+df['R'] + df['RBI']-df['CS']-df['GDP']
    df['O%'] = round(df['O']/df['PA']*100,1)
    return(df)

def hit_rate_stats(df):
    df['avg'] = round(df['H']/df['AB'],3)
    df['obp'] = round((df['H']+df['BB']+df['HBP'])/(df['AB']+df['BB']+df['HBP']+df['SF']),3)
    df['slg'] = round((df['H']+df['2B']+2*df['3B']+3*df['HR'])/df['AB'],3)
    df['ops'] = df['obp']+df['slg']
    df['K%'] = round(df['SO']/df['PA']*100,1)
    df['BB%'] = round(df['BB']/df['PA']*100,1)
    df['BABIP'] = round((df['H']-df['HR'])/(df['AB']-df['HR']-df['SO']+df['SF']),3)
    return(df)

def team_hit_display(tm,lg,qual=1):
    ''' prints hitters for team in a league having at least qual PA, along with team totals for these qualified hitters'''
    hit_count_stats = ['G','PA','AB','H','2B','3B','HR','BB','HBP','SF','IBB','SO','R','RBI','SB','CS','SH','GDP','O']
    hh = hit[(hit[lg]==tm)&(hit['PA']>=qual)][['Name']+hit_count_stats].sort_values('O',ascending=False).fillna(0)
    hh.loc['Team']= hh.sum()
    hh['DMB']=tm
    hh.iloc[-1,0]="Team"
    hh = hit_rate_stats(hh)
    hit_summary_columns = ['G','PA','O','HR','R','RBI','avg','obp','slg','ops','K%','BB%','O%','BABIP']

    return(hh[['Name','DMB']+hit_summary_columns]) 



