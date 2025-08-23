=> General 
1) remove the emoji and remplacing by icons
2) translating in french ?
3) documentatiing in french 
- business part
- + coding part
4) be careful with UTF-8

5) PROCESSING
* filter : 
number of minutes  
number of games

creer processing_v3 pour drop definitiveemnt les joueuss nba, where position = unknown alors drop
Dorka Juhász

=> nav bar make it look better

=> home page
bookmark 1: conf standing
remove TM
bookmark 4 : salaries
adding a sentence stating : find quickly about salary insign for team and/or player

=> team
1) bookmark team stats
- adding more spaces between the KPI in horizontals
- full team : to add an icon
- changing the field parameters : pre selecting some column or pre removing some of them : PLAYER_ID, TM, NICKNAME, TEAM_ABBREVIATION

2) bookmark team salaries
- adding more spaces between the KPI in horizontals
- in documentation : writting the fact that the data contains null values = one of its limits
- later for me changing the best value calculation (not priority)


=> statistics 
1) make the barchart look better
2) removing repeated labels 
 instead ofhaving two : (Regular Season - Per Game)
we should have one as a title is better and its same for playoff
🏀 Offensive Statistics (Regular Season - Per Game)
🛡️ Defensive Statistics (Regular Season - Per Game)
🏀 Offensive Statistics (Regular Season - Total)
🛡️ Defensive Statistics (Regular Season - Total)

3)
* add export to excel button
* filter

4) full data
- changing the field parameters : pre selecting some column or pre removing some of them : PLAYER_ID, TM, NICKNAME, TEAM_ABBREVIATION
- 📊 Playoffs — Full Data (Field Parameter Style) => removing : (Field Parameter Style) 
- 📊  Regular Season — Full Data (Field Parameter Style) => removing : (Field Parameter Style) 


=> champ historic

1) making the barchart look better and adding a title like "historic insight"




=> processing_v2

"""
drop duplicates
   PLAYER_ID          PLAYER_NAME   TM  ... STL_PG BLK_PG PLUS_MINUS_PG
0      1630639          A.J. Lawson  TOR  ...    0.5    0.2          -0.7  
1      1630639          A.J. Lawson  DAL  ...    1.2    0.2          -3.8  
4      1642358           AJ Johnson  WAS  ...    0.4    0.1          -5.2  
5      1642358           AJ Johnson  MIL  ...    0.6    0.4          -6.6  

"""

df_positions = df_positions.drop_duplicates(subset=["PLAYER_ID"], keep="last")

"""
Why "last"?

Because when you concatenate all the rosters (pos_frames), the order of players depends on the order you loop over the teams.

If a player was traded (e.g. Kevin Durant moved from Brooklyn to Phoenix in the past), he could appear twice: once in the Nets roster, once in the Suns roster.

After concatenation, the last team processed will overwrite the earlier one. So keep="last" means:
→ keep the most recent roster entry for that player.

Example

df_positions before dedupe:

PLAYER_ID	PLAYER	TEAM	POSITION
201142	Kevin Durant	BKN	F
201142	Kevin Durant	PHX	F-G
df_positions.drop_duplicates(subset=["PLAYER_ID"], keep="last")


Result:

PLAYER_ID	PLAYER	TEAM	POSITION
201142	Kevin Durant	PHX	F-G

We kept the last one → PHX roster.
"""
