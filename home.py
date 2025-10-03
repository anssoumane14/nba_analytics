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
    "flat_rs_player": load_flat("flat_rs_player"),  # 🔹 added for Top Players
    "flat_team_per_poss_stats": load_flat("flat_team_per_poss_stats"),
    "flat_all_nba_teams": load_flat("flat_all_nba_teams"),
    "flat_all_def_teams": load_flat("flat_all_def_teams"),
    "flat_all_rookie_teams": load_flat("flat_all_rookie_teams"),
    "flat_salaries_2026": load_flat("flat_salaries_2026"),  
}

# -------------------------------
# Title
# -------------------------------
st.markdown("<h1 style='text-align: center;'>NBA Dashboard</h1>", unsafe_allow_html=True)

# -------------------------------
# Season Selector
# -------------------------------
all_seasons = set()
for df in flats.values():
    if "SEASON" in df.columns:
        all_seasons.update(df["SEASON"].dropna().unique())

if all_seasons:
    season_filter = st.selectbox("Select a season", sorted(all_seasons, reverse=True))
else:
    season_filter = None
    st.warning("No seasons available in the flat tables")

# -------------------------------
# KPI Awards (MVP, ROY, Leaders)
# -------------------------------
if not flats["flat_awards"].empty and season_filter:
    st.markdown("## Awards Overview")
    display_awards_kpi(flats["flat_awards"], season_filter)

# -------------------------------
# Tabs
# -------------------------------

# Add All-Star Teams Tab
# -------------------------------
tab_conf, tab_top_players, tab_honors, tab_salaries, tab_all_star = st.tabs([
    "Conference Standings",
    "Top Players",
    "Honors",
    "Salaries",
    "All-Star Teams"
])
# -------------------------------
# Conference Standings Tab
# -------------------------------
with tab_conf:
    st.markdown("<p style='font-size:12px; color:gray;'>* For playoff teams</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Eastern Conference
    with col1:
        df_east = flats["flat_east_standing"].copy()
        if not df_east.empty:
            df_east = df_east.rename(columns={"EASTERN_CONFERENCE": "TEAM"})
            df_east = df_east[~df_east["TEAM"].str.contains("Division", case=False, na=False)]
            
            if season_filter:
                df_east = df_east[df_east["SEASON"] == season_filter]

            cols_east = ["TEAM", "W", "L", "W/L%", "GB", "SEASON"]
            st.markdown("### Eastern Conference")
            st.dataframe(df_east[cols_east], hide_index=True, use_container_width=True)
        else:
            st.info("No Eastern Conference data available.")

    # Western Conference
    with col2:
        df_west = flats["flat_west_standing"].copy()
        if not df_west.empty:
            df_west = df_west.rename(columns={"WESTERN_CONFERENCE": "TEAM"})
            df_west = df_west[~df_west["TEAM"].str.contains("Division", case=False, na=False)]
            
            if season_filter:
                df_west = df_west[df_west["SEASON"] == season_filter]

            cols_west = ["TEAM", "W", "L", "W/L%", "GB", "SEASON"]
            st.markdown("### Western Conference")
            st.dataframe(df_west[cols_west], hide_index=True, use_container_width=True)
        else:
            st.info("No Western Conference data available.")

# -------------------------------
# Top Players Tab
# -------------------------------
with tab_top_players:
    st.markdown("## Top 3 Players by Key Metrics (Regular Season Only)")

    df_players = flats["flat_rs_player"].copy()

    if not df_players.empty:
        if season_filter:
            df_players = df_players[df_players["SEASON"] == season_filter]

        # Filtering out players with too few games/minutes
        if "G" in df_players.columns and "MP" in df_players.columns:
            df_players = df_players[(df_players["G"] > 10) & (df_players["MP"] > 100)]

        all_teams = sorted(df_players["TEAM"].dropna().unique())
        team_choice = st.selectbox(
            "Select Team",
            options=["All Teams"] + all_teams,
            index=0,
            key="top_players_team_filter"
        )

        df_tp = df_players.copy()
        if team_choice != "All Teams":
            df_tp = df_tp[df_tp["TEAM"] == team_choice]

        metrics = {
            "Points Per Game": "PTS_PG",
            "Rebounds Per Game": "TRB_PG",
            "Assists Per Game": "AST_PG"
        }

        for label, col_name in metrics.items():
            if col_name in df_tp.columns:
                top3 = (
                    df_tp[["PLAYER", "TEAM", col_name]]
                    .sort_values(by=col_name, ascending=False)
                    .head(3)
                )
                st.markdown(f"### {label}")
                st.dataframe(top3, hide_index=True, use_container_width=True)
    else:
        st.info("No regular season player data available for this season.")

# -------------------------------
# Honors Tab
# -------------------------------
with tab_honors:
    st.markdown("## Honors")

    # === All-NBA Teams ===
    df_all_nba = flats["flat_all_nba_teams"].copy()
    if not df_all_nba.empty:
        if season_filter:
            df_all_nba = df_all_nba[df_all_nba["SEASON"] == season_filter]

        st.markdown("### All-NBA Teams")
        cols_to_show = []
        for c in ["1ST_TEAM", "2ND_TEAM", "3RD_TEAM", "SEASON"]:
            if c in df_all_nba.columns and not df_all_nba[c].isna().all():
                cols_to_show.append(c)

        st.dataframe(df_all_nba[cols_to_show], hide_index=True, use_container_width=True)
    else:
        st.info("No All-NBA Teams data available.")

    # === All-Defensive Teams ===
    df_all_def = flats["flat_all_def_teams"].copy()
    if not df_all_def.empty:
        if season_filter:
            df_all_def = df_all_def[df_all_def["SEASON"] == season_filter]

        st.markdown("### All-Defensive Teams")
        cols_to_show = []
        for c in ["1ST_TEAM", "2ND_TEAM", "SEASON"]:
            if c in df_all_def.columns and not df_all_def[c].isna().all():
                cols_to_show.append(c)

        st.dataframe(df_all_def[cols_to_show], hide_index=True, use_container_width=True)
    else:
        st.info("No All-Defensive Teams data available.")

    # === All-Rookie Teams ===
    df_all_rookie = flats["flat_all_rookie_teams"].copy()
    if not df_all_rookie.empty:
        if season_filter:
            df_all_rookie = df_all_rookie[df_all_rookie["SEASON"] == season_filter]

        st.markdown("### All-Rookie Teams")
        cols_to_show = []
        for c in ["1ST_TEAM", "2ND_TEAM", "SEASON"]:
            if c in df_all_rookie.columns and not df_all_rookie[c].isna().all():
                cols_to_show.append(c)

        st.dataframe(df_all_rookie[cols_to_show], hide_index=True, use_container_width=True)
    else:
        st.info("No All-Rookie Teams data available.")

# -------------------------------
# Salaries Tab
# -------------------------------

from functions import map_team_names 

# -------------------------------
# Salaries Tab
# -------------------------------
with tab_salaries:
    st.markdown("## Salaries")
    st.markdown(
        "<p style='font-size:14px; color:gray;'>This table represents the latest update of NBA player contracts starting from the 2025-26 season.</p>",
        unsafe_allow_html=True
    )

    df_salaries = flats["flat_salaries_2026"].copy()

    # Drop last column if it's useless (-9999)
    if df_salaries.columns[-1] == "-9999":
        df_salaries = df_salaries.iloc[:, :-1]

    if df_salaries.empty:
        st.info("No salaries data available.")
    else:
        # Normalize column names
        df_salaries = df_salaries.rename(columns={
            "Player": "PLAYER",
            "Tm": "TM"
        })

        # ✅ Add full team name
        df_salaries = map_team_names(df_salaries, abbr_col="TM")

        TEAM_ALL, PLAYER_ALL = "All Teams", "All Players"

        # === Team filter ===
        team_options = [TEAM_ALL] + sorted(df_salaries["TEAM"].dropna().unique())
        team_sel = st.selectbox("Team", team_options, index=0, key="sal_team")

        # === Player filter ===
        if team_sel == TEAM_ALL:
            player_options = [PLAYER_ALL] + sorted(df_salaries["PLAYER"].dropna().unique())
        else:
            player_options = [PLAYER_ALL] + sorted(
                df_salaries.loc[df_salaries["TEAM"] == team_sel, "PLAYER"].dropna().unique()
            )

        prev_player = st.session_state.get("sal_player", PLAYER_ALL)
        player_index = player_options.index(prev_player) if prev_player in player_options else 0
        player_sel = st.selectbox("Player", player_options, index=player_index, key="sal_player")

        # === Apply filters ===
        df_filtered = df_salaries.copy()
        if team_sel != TEAM_ALL:
            df_filtered = df_filtered[df_filtered["TEAM"] == team_sel]
        if player_sel != PLAYER_ALL:
            df_filtered = df_filtered[df_filtered["PLAYER"] == player_sel]

        # === Display ===
        if df_filtered.empty:
            st.info("No results for these filters.")
        else:
            # Drop TM (acronym) for display
            if "TM" in df_filtered.columns:
                df_filtered = df_filtered.drop(columns=["TM"])

            # Reorder columns so TEAM (full name) is right after PLAYER
            cols = df_filtered.columns.tolist()
            if "PLAYER" in cols and "TEAM" in cols:
                cols.remove("TEAM")
                player_index = cols.index("PLAYER")
                cols.insert(player_index + 1, "TEAM")
                df_filtered = df_filtered[cols]

            st.dataframe(df_filtered, hide_index=True, use_container_width=True)



# -------------------------------
# All-Star Teams Tab
# -------------------------------
with tab_all_star:
    st.markdown("## All-Star Teams")

    if season_filter:
        # Extraire uniquement l'année de début (ex: '2016-17' -> '2016')
        year_str = str(season_filter).split("-")[0]
        path_allstar = f"raw_data/all_star_teams/all_star_teams_{year_str}.csv"

        if os.path.exists(path_allstar):
            try:
                df_all_star = pd.read_csv(path_allstar, encoding="utf-8-sig")
                if not df_all_star.empty:
                    st.dataframe(df_all_star, hide_index=True, use_container_width=True)
                else:
                    st.info("All-Star data is empty for this season.")
            except Exception as e:
                st.error(f"Error loading All-Star data: {e}")
        else:
            st.info(f"No All-Star file found for {season_filter}.")
    else:
        st.info("Please select a season to view All-Star Teams.")