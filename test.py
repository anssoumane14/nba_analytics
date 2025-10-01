import pandas as pd
import re
import streamlit as st

from stat_functions import (
    afficher_offensif_v2,
    afficher_defensif_v2,
    graphique_barres_v2,
    pick_display_columns,
    compute_player_career_stats,
    display_kpi_cards,
    compare_rs_vs_po,
    compare_seasons 
)

import plotly.express as px

# -------------------------------
# Clean player names
# -------------------------------
def clean_player_names(df: pd.DataFrame) -> pd.DataFrame:
    if "PLAYER" in df.columns:
        df["PLAYER"] = df["PLAYER"].astype(str).apply(lambda x: re.sub(r"\*", "", x).strip())
    return df

st.set_page_config(layout="wide")

# -------------------------------
# Load Data
# -------------------------------
df_rs = pd.read_csv("flat_table/flat_rs_player.csv", encoding="utf-8-sig")
df_po = pd.read_csv("flat_table/flat_po_player.csv", encoding="utf-8-sig")

df_rs = clean_player_names(df_rs)
df_po = clean_player_names(df_po)

# -------------------------------
# Title
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>NBA Statistics</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align: center; color: gray;'>The numbers behind the performances</h3>", 
    unsafe_allow_html=True
)

# -------------------------------
# Tabs
# -------------------------------
tab_basic, tab_advanced = st.tabs(["Basic Statistics", "Player Analytics"])


# ===============================
# I. BASIC STATISTICS
# ===============================
with tab_basic:
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1], gap="large")

    with col1:
        metric_filter = st.selectbox(
            "Choose a view", 
            ["Leaders", "Top 30", "All Data"],
            key="metric_filter"
        )

    with col2:
        season_filter = st.radio(
            "Season Part", 
            ["Regular Season", "Playoffs"], 
            horizontal=True,
            key="season_filter"
        )

    with col3:
        df_temp = df_rs if season_filter == "Regular Season" else df_po
        seasons = sorted(df_temp["SEASON"].unique(), reverse=True)
        season_choice = st.selectbox("Season", seasons, key="season_choice")

    with col4:
        stat_mode = st.radio(
            "Statistic Mode", 
            ["Per Game", "Total"], 
            horizontal=True,
            key="stat_mode"
        )

    # Force display as table only (disable bar chart for now)
    view_mode = "Tableau"

    df = df_rs if season_filter == "Regular Season" else df_po
    df = df[(df["SEASON"] == season_choice) & (df["G"] > 10) & (df["MP"] > 100)]

    # Leaders
    if metric_filter == "Leaders":
        afficher_offensif_v2(df, season_choice, stat_mode, view_mode)
        st.divider()
        afficher_defensif_v2(df, season_choice, stat_mode, view_mode)

    # Top 30
    elif metric_filter == "Top 30":
        stat_choice = st.selectbox(
            "Select a statistic",
            ["Points", "Assists", "Total Rebounds", "Offensive Rebounds",
             "Defensive Rebounds", "Minutes", "3-Pointers Made", "Free Throws Made",
             "Blocks", "Steals", "Turnovers"]
        )
        stat_map = {
            "Points": "PTS",
            "Assists": "AST",
            "Total Rebounds": "TRB",
            "Offensive Rebounds": "ORB",
            "Defensive Rebounds": "DRB",
            "Minutes": "MP",
            "3-Pointers Made": "3P",
            "Free Throws Made": "FT",
            "Blocks": "BLK",
            "Steals": "STL",
            "Turnovers": "TOV",
        }

        suffix = "_PG" if stat_mode == "Per Game" else ""
        chosen_col = stat_map[stat_choice] + suffix

        top30 = df[["PLAYER", "TEAM", chosen_col]].sort_values(by=chosen_col, ascending=False).head(30)

        st.markdown(f"## Top 30 {stat_choice} ({stat_mode}) - {season_choice} ({season_filter})")

        st.dataframe(top30, hide_index=True, use_container_width=True)

        # Disabled bar chart for now
        # fig = graphique_barres_v2(top30, chosen_col, f"Top 30 {stat_choice}")
        # st.plotly_chart(fig, use_container_width=True)

    # All data
    elif metric_filter == "All Data":
        st.markdown(f"## {season_filter} — Complete Data ({season_choice})")

        cols = pick_display_columns(df, key="all_data_cols")
        st.dataframe(df[cols], hide_index=True, use_container_width=True)


# ===============================
# II. PLAYER ANALYTICS
# ===============================
with tab_advanced:
    # -------------------------------
    # KPI CARDS
    # -------------------------------
    st.markdown("### Player Analytics")

    col1, col2 = st.columns(2)

    with col1:
        season_type_choice = st.radio(
            "Select Season Type", ["Regular Season", "Playoffs"],
            horizontal=True, key="analytics_season_type"
        )
    with col2:
        player_choice = st.selectbox(
            "Select a player", sorted(df_rs["PLAYER"].unique()), key="analytics_player"
        )

    df_source = df_rs if season_type_choice == "Regular Season" else df_po

    st.markdown(f"#### {player_choice}'s Career ({season_type_choice})")

    # === Nouveau KPI : total de matchs joués ===
    total_games = df_source[df_source["PLAYER"] == player_choice]["G"].sum()
    st.metric(label="Total Games Played", value=total_games)

    # KPIs existants
    display_kpi_cards(df_source, player_choice, season_type_choice)


    # -------------------------------
    # BAR CHART COMPARISONS
    # -------------------------------
    st.markdown("### Performance Comparisons")

    # Graph 1 : RS vs PO (same season)
    st.subheader("Regular Season vs Playoffs (same season)")
    col1, col2 = st.columns(2)
    with col1:
        player_choice = st.selectbox("Select a player", sorted(df_rs["PLAYER"].unique()), key="comp_rs_po_player")
    with col2:
        season_choice = st.selectbox("Select a season", sorted(df_rs["SEASON"].unique(), reverse=True), key="comp_rs_po_season")

    compare_rs_vs_po(df_rs, df_po, player_choice, season_choice)

    # Graph 2 : RS season vs RS season
    st.subheader("Compare Regular Season across two seasons")
    col1, col2, col3 = st.columns(3)
    with col1:
        player_choice_rs = st.selectbox("Select a player", sorted(df_rs["PLAYER"].unique()), key="comp_rs_player")
    with col2:
        season1_rs = st.selectbox("Season 1", sorted(df_rs["SEASON"].unique(), reverse=True), key="comp_rs_season1")
    with col3:
        season2_rs = st.selectbox("Season 2", sorted(df_rs["SEASON"].unique(), reverse=True), key="comp_rs_season2")

    if season1_rs != season2_rs:
        compare_seasons(df_rs, player_choice_rs, season1_rs, season2_rs, context_label="Regular Season")

    # Graph 3 : PO season vs PO season
    st.subheader("Compare Playoffs across two seasons")
    col1, col2, col3 = st.columns(3)
    with col1:
        player_choice_po = st.selectbox("Select a player", sorted(df_po["PLAYER"].unique()), key="comp_po_player")
    with col2:
        season1_po = st.selectbox("Season 1", sorted(df_po["SEASON"].unique(), reverse=True), key="comp_po_season1")
    with col3:
        season2_po = st.selectbox("Season 2", sorted(df_po["SEASON"].unique(), reverse=True), key="comp_po_season2")

    if season1_po != season2_po:
        compare_seasons(df_po, player_choice_po, season1_po, season2_po, context_label="Playoffs")
