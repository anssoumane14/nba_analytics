
=> NBA STATICS
* add export to excel button
* filter

=> PROCESSING
* filter : 
number of minutes  
number of games

creer processing_v3 pour drop definitiveemnt les joueuss nba, where position = unknown alors drop
Dorka Juhász


=> NBA CHAMPION
* in df_nba_champion
drop lg column

""".



### ⏱ 4. **Decade-wise Analysis**

* Radio filter: 1980s, 1990s, 2000s, 2010s, 2020s.
* Show:

  * Most dominant team in that decade
  * MVP leaders
  * Titles count per decade
    👉 Great for storytelling about NBA dynasties.

---

### 📈 7. **Team Head-to-Head in Finals**

* Matrix/table to show which teams faced each other most in the Finals.
* Ex: Lakers vs Celtics 🔥.

---

### 👑 8. **Players with the Highest Finals Points / Rebounds / Assists**

* Show records for players in Finals performances.
* Could add a **Top Performance card** (e.g., "Most points in a Finals series").


"""


=> HOME
* 


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
