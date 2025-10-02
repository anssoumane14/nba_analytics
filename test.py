# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

from nav_bar import show_navbar
from stat_functions import display_awards_kpi

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="NBA Dashboard", layout="wide")

# -------------------------------
# Navigation Bar
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
# Load all flat tables
# -------------------------------
flats = {
    "flat_awards": load_flat("flat_awards"),
    "flat_east_standing": load_flat("flat_east_standing"),
    "flat_west_standing": load_flat("flat_west_standing"),
    "flat_team_per_poss_stats": load_flat("flat_team_per_poss_stats"),
    "flat_all_nba_teams": load_flat("flat_all_nba_teams"),
    "flat_all_def_teams": load_flat("flat_all_def_teams"),
    "flat_all_rookie_teams": load_flat("flat_all_rookie_teams"),
     #"flat_salaries": load_flat("flat_salaries"),  # example denormalized salaries
}

# -------------------------------
# Title
# -------------------------------
st.markdown("<h1 style='text-align: center;'>🏀 NBA Dashboard</h1>", unsafe_allow_html=True)

# -------------------------------
# Season Selector
# -------------------------------
all_seasons = set()
for df in flats.values():
    if "SEASON" in df.columns:
        all_seasons.update(df["SEASON"].dropna().unique())

if all_seasons:
    season_filter = st.selectbox("🔎 Select a season", sorted(all_seasons, reverse=True))
else:
    season_filter = None
    st.warning("⚠️ No seasons available in the flat tables")

# -------------------------------
# KPI Awards (MVP, ROY, Leaders)
# -------------------------------
if not flats["flat_awards"].empty and season_filter:
    st.markdown("## 🏆 Awards Overview")
    display_awards_kpi(flats["flat_awards"], season_filter)

# -------------------------------
# Tabs
# -------------------------------
tab_conf, tab_eval, tab_honors, tab_awards, tab_salaries = st.tabs([
    "Conference Standings",
    "Team Evaluations",
    "Honors",
    "Awards",
    "Salaries"
])

# -------------------------------
# Conference Standings Tab
# -------------------------------
with tab_conf:
    # TODO: Show East/West standings
    pass

# -------------------------------
# Team Evaluations Tab
# -------------------------------
with tab_eval:
    # TODO: Show ORTG / DRTG / NRTG
    pass

# -------------------------------
# Honors Tab
# -------------------------------
with tab_honors:
    # TODO: Show All-NBA / All-Defensive / All-Rookie Teams
    pass

# -------------------------------
# Awards Tab
# -------------------------------
with tab_awards:
    # TODO: Show raw awards table
    pass

# -------------------------------
# Salaries Tab
# -------------------------------
with tab_salaries:
    # TODO: Show player salaries (denormalized)
    pass

