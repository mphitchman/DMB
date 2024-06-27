A streamlit app for scraping MLB stats for players according to their teams in DMB baseball.

Files: 

`main_scrape.py` scrapes the key data tables hit24, pit24 and stores them in the csv folder

`csv/keyID.csv` is the player lookup table matching a player's playerIDs from various sites, and listing their team for various DMB leagues. 
  - `Name`, player name
  - `key_DMB`, player universal ID (UID) in Diamond Mind Baseball (DMB)
  - `key_FG`, fangraphs player id
  - `key_MLB`, mlb player id
  - `key_bbref`, baseball reference player id 
  - `type`, primary role, "P" for pitcher, "B" for batter (Shohei Ohtani listed twice, once for each type)
  - `RJML`, `SSBL`, `CJPL`, a player's team in these respective DMB leagues

`app.py` - the streamlit app for the RJML  [Link to app](https://rjml-mlb24.streamlit.app) If the app is snoozing, feel free to wake it up!

`app_all_leagues.py` - streamlit app for all three leagues. [Link to app](https://dmb-mlb24.streamlit.app) If the app is snoozing, feel free to wake it up!

    