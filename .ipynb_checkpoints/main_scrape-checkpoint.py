import pybaseball as pyb
import pandas as pd
from datetime import datetime

def load_key():
    return(pd.read_csv("https://mphitchman.com/DMB/csv/keyID.csv"))

def load_hit():
    df = pyb.fg_batting_data(start_season=2024,qual=10)
    df = df.rename(columns={"IDfg": "key_FG","Team":"MLB"})
    df = df.merge(keyID[keyID['type']=="B"][['type','key_FG','RJML','SSBL','CJPL']],on="key_FG",how='left').set_index('Name')
    return(df)

def load_fielding():
    return(pyb.fielding_stats(start_season='2024',qual=3))
   

def load_pit():
    pf = pyb.pitching_stats_bref() #baseball reference scrape to get stats needed for ops and rc
    pf = pf.rename(columns={"mlbID": "key_MLB"})
    pf["key_MLB"] = pd.to_numeric(pf["key_MLB"])
    df = pyb.fg_pitching_data(start_season=2024,qual=10)
    df = df.rename(columns={"IDfg": "key_FG","Team":"MLB"})
    df = df.merge(keyID[keyID['type']=="P"][['type','key_FG','key_MLB','RJML','SSBL','CJPL']],on="key_FG",how='left')
    df = df.merge(pf[['BF','AB','2B','3B','SF','GDP','SB','CS','key_MLB']],on='key_MLB',how='left')
    return(df.set_index('Name'))

def add_O(df):
    df['O'] = df['H']+df['2B']+2*df['3B']+2*df['HR']+df['BB']+df['SB']+df['SH']+df['R'] + df['RBI']-df['CS']-df['GDP']
    return(df)

def IP_to_Inn(x):
    import numpy as np
    return(np.floor(x)+10*(x-np.floor(x))/3)

def positions_played(keyFG):
    '''assumes you've defined the dataframe 'fld' via fld = load_fielding()'''
    if keyFG not in fld['IDfg'].tolist():
        return("-")
    else:
        df = fld[fld['IDfg'] == keyFG].sort_values(by="Inn",ascending=False)
        pos_list = df['Pos'].tolist()
        pos_dict = {'C':'2', '1B':'3', '2B':'4', '3B':'5', 'SS':'6', 'LF':'7', 'CF':'8', 'RF':'9','P':''}
        pos_num = list((pd.Series(pos_list)).map(pos_dict))
        return(",".join(pos_num))

#### scrape

scrape_date = datetime.today().strftime('%Y-%m-%d')
keyID=load_key()
hit24 = add_O(load_hit())
hit24['date']=scrape_date
fld = load_fielding()
hit24['Pos'] = hit24['key_FG'].apply(positions_played)
pit24 = load_pit()
pit24['Inn'] = pit24['IP'].apply(IP_to_Inn)
hit24.to_csv("csv/hit24.csv")
pit24.to_csv("csv/pit24.csv")
print("hit24 and pit24 updated and saved to csv folder on "+scrape_date)
