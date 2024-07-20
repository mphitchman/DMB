A streamlit app for showing current MLB stats for players grouped by teams in a Diamond Mind Baseball league.

Files: 

`main_scrape.py` scrapes the key data tables hit24, pit24 and stores them in the csv folder

`csv/keyID.csv` is the player lookup table with these columns: 
  - `Name`, player name
  - `key_DMB`, player universal ID (UID) in Diamond Mind Baseball (DMB)
  - `key_FG`, fangraphs player id
  - `key_MLB`, mlb player id
  - `key_bbref`, baseball reference player id 
  - `type`, primary role, "P" for pitcher, "B" for batter (Shohei Ohtani listed twice, once for each type)
  - `RJML`, `SSBL`, `CJPL`, a player's team in these respective DMB leagues

`app.py` - the streamlit app for the RJML  [Link to app](https://rjml-mlb24.streamlit.app) If the app is snoozing, feel free to wake it up!

`app_all_leagues.py` - streamlit app for all three leagues. [Link to app](https://dmb-mlb24.streamlit.app) Feel free to contact me if you would like your DMB league added to the list!

    
