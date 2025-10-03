# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

from nav_bar import show_navbar
from stat_functions import render_kpi, pick_display_columns

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Team Overview", layout="wide")

# -------------------------------
# Navigation bar
# -------------------------------
show_navbar()

# -------------------------------
# Load Data Helpers (cached)
# -------------------------------
FLAT_BASE = "flat_table"

@st.cache_data(ttl=3600, show_spinner=False)
def load_flat(name: str) -> pd.DataFrame:
    path = f"{FLAT_BASE}/{name}.csv"
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")

# -------------------------------
# Load data
# -------------------------------
df_reg_players = load_flat("flat_rs_player")
df_east = load_flat("flat_east_standing")
df_west = load_flat("flat_west_standing")

# -------------------------------
# Utils
# -------------------------------
def keep_last_team(team_str: str) -> str:
    if pd.isna(team_str):
        return None
    return str(team_str).split("/")[-1].strip()

# -------------------------------
# Title + Season Selector
# -------------------------------
st.markdown("<h1 style='text-align: center;'>NBA Team Overview</h1>", unsafe_allow_html=True)

all_seasons = sorted(df_reg_players["SEASON"].dropna().unique()) if "SEASON" in df_reg_players.columns else []
season_filter = st.selectbox("Select a Season", all_seasons, index=len(all_seasons)-1 if all_seasons else 0)

# Filter by season
if season_filter:
    df_reg_players = df_reg_players[df_reg_players["SEASON"] == season_filter]
    df_west = df_west[df_west["SEASON"] == season_filter]
    df_east = df_east[df_east["SEASON"] == season_filter]

# -------------------------------
# Team Selector
# -------------------------------
df_reg_players["TEAM_CLEAN"] = df_reg_players["TEAM"].apply(keep_last_team)
team_options = sorted(df_reg_players["TEAM_CLEAN"].dropna().unique())
selected_team = st.selectbox("Select a Team", team_options, index=0, key="team_filter")
# -------------------------------
# Standings
# -------------------------------
if not df_east.empty and "EASTERN_CONFERENCE" in df_east.columns:
    df_east["PLAYOFF_TEAM"] = df_east["EASTERN_CONFERENCE"].str.contains(r"\*", regex=True).map({True: "Yes", False: "No"})
    df_east["EASTERN_CONFERENCE"] = df_east["EASTERN_CONFERENCE"].str.replace(r"\*", "", regex=True).str.strip()

if not df_west.empty and "WESTERN_CONFERENCE" in df_west.columns:
    df_west["PLAYOFF_TEAM"] = df_west["WESTERN_CONFERENCE"].str.contains(r"\*", regex=True).map({True: "Yes", False: "No"})
    df_west["WESTERN_CONFERENCE"] = df_west["WESTERN_CONFERENCE"].str.replace(r"\*", "", regex=True).str.strip()

df_west_local = df_west.rename(columns={"WESTERN_CONFERENCE": "TEAM"}).copy()
df_east_local = df_east.rename(columns={"EASTERN_CONFERENCE": "TEAM"}).copy()
df_west_local["CONF"] = "West"
df_east_local["CONF"] = "East"
df_west_local["RANK"] = range(1, len(df_west_local) + 1)
df_east_local["RANK"] = range(1, len(df_east_local) + 1)
df_standings = pd.concat([df_east_local, df_west_local], ignore_index=True)

team_row = df_standings[df_standings["TEAM"] == selected_team]
if not team_row.empty:
    conf = team_row.iloc[0]["CONF"]
    rank = int(team_row.iloc[0]["RANK"])
    playoff_flag = team_row.iloc[0]["PLAYOFF_TEAM"]  # déjà "Yes"/"No"
    st.markdown(f"**Conference:** {conf} — **Rank:** #{rank} — **Playoffs:** {playoff_flag}")
else:
    st.warning(f"{selected_team} not found in standings!")



# -------------------------------
# Team Statistics
# -------------------------------
df_current = df_reg_players[df_reg_players["TEAM_CLEAN"] == selected_team]
st.markdown(f"### Team Statistics — {selected_team} ({season_filter})")

# KPIs
c1, c2, c3 = st.columns(3)
with c1: render_kpi(df_current, "PTS_PG", "Points Per Game")
with c2: render_kpi(df_current, "TRB_PG", "Rebounds Per Game")
with c3: render_kpi(df_current, "AST_PG", "Assists Per Game")

st.markdown("<br>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)
with c4: render_kpi(df_current, "STL_PG", "Steals Per Game")
with c5: render_kpi(df_current, "BLK_PG", "Blocks Per Game")
with c6: render_kpi(df_current, "TOV_PG", "Turnovers Per Game")

st.markdown("<br><br>", unsafe_allow_html=True)

# Full roster
st.markdown("### Full Roster")
cols_to_show = pick_display_columns(
    df_current,
    base_cols=("TEAM", "PLAYER", "PTS_PG", "AST_PG", "TRB_PG", "MP_PG"),
    exclude=("PLAYER_ID", "RK", "TEAM_CLEAN"),
    key="team_stats_columns"
)
if cols_to_show:
    st.dataframe(df_current[cols_to_show], hide_index=True, use_container_width=True)
else:
    st.info("No columns selected.")
