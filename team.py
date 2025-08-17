# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
import plotly.express as px  # optional for future charts

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Team", layout="wide")

# -------------------------------
# Load Data
# -------------------------------
df_west = pd.read_excel("data/df_western_conf_standing.xlsx")
df_east = pd.read_excel("data/df_eastern_conf_standing.xlsx")
df_team_ratings = pd.read_excel("data/df_nba_team_reg_season_ratings.xlsx")
df_reg_players = pd.read_excel("data/df_reg_season_players.xlsx")
df_po_players = pd.read_excel("data/df_playoff_players.xlsx")
df_salaries = pd.read_excel("data/df_nba_players_salaries.xlsx")

# -------------------------------
# Function
# -------------------------------
def render_kpi(df, value_col, title):
    if df.empty or value_col not in df.columns or df[value_col].dropna().empty:
        st.info(f"No data for {title}.")
        return

    idx = df[value_col].idxmax()
    row = df.loc[idx]
    val = float(row[value_col])
    player_name = str(row.get("PLAYER_NAME", "Unknown"))
    team_name = str(row.get("TEAM", row.get("TEAM_ABBREVIATION", "")))

    width_px = 320
    st.markdown(
        f"""
        <div style="background:#111827; color:#e5e7eb; padding:16px; border-radius:12px; width:{width_px}px;">
            <div style="font-size:14px; opacity:.85; margin-bottom:6px; text-align:center;">{title}</div>
            <div style="font-size:32px; font-weight:700; line-height:1; text-align:center;">{val:.1f}</div>
            <div style="font-size:13px; opacity:.9; margin-top:6px; text-align:center;">{player_name} <span style="opacity:.7">({team_name})</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# Title
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>🏀 NBA TEAM 2024-25 Overview</h1>",
    unsafe_allow_html=True
)

# -------------------------------
# Global Team Filter
# -------------------------------
team_options = sorted(df_reg_players["TEAM"].dropna().unique())
selected_team = st.selectbox("Select a Team", team_options, index=0, key="team_filter")

# -------------------------------
# Build combined standings with flags + rank
# -------------------------------
df_west_local = df_west.copy()
df_east_local = df_east.copy()

df_west_local["CONF"] = "West"
df_east_local["CONF"] = "East"

# If your standings are already sorted, rank is row order
df_west_local["RANK"] = range(1, len(df_west_local) + 1)
df_east_local["RANK"] = range(1, len(df_east_local) + 1)

df_standings = pd.concat([df_east_local, df_west_local], ignore_index=True)

def to_bool_playoff(x):
    s = str(x).strip().lower()
    return s in ("*", "true", "1")

if "PLAYOFF_TEAM" in df_standings.columns:
    if df_standings["PLAYOFF_TEAM"].dtype != bool:
        df_standings["PLAYOFF_TEAM"] = df_standings["PLAYOFF_TEAM"].apply(to_bool_playoff)
else:
    df_standings["PLAYOFF_TEAM"] = False

# Lookup selected team rank
team_row = df_standings[df_standings["TEAM"] == selected_team]
if not team_row.empty:
    conf = team_row.iloc[0]["CONF"]
    rank = int(team_row.iloc[0]["RANK"])
    st.markdown(f"**Conference:** {conf} — **Rank:** #{rank}")
else:
    st.info("Selected team not found in standings.")

# -------------------------------
# Tabs (Bookmarks)
# -------------------------------
tab_stats, tab_salaries = st.tabs(["📊 Team Stats", "💰 Salaries"])

# ===============================
# 📊 Team Stats
# ===============================
with tab_stats:
    season_filter = st.radio(
        "Season Type",
        ["Regular Season", "Playoffs"],
        horizontal=True,
        key="season_filter_team"
    )

    # Select correct dataset for the season
    df = df_reg_players if season_filter == "Regular Season" else df_po_players

    # Apply global team filter
    df = df[df["TEAM"] == selected_team]

    # If Playoffs selected but team did not make playoffs, stop this tab gracefully
    if season_filter == "Playoffs":
        row = df_standings[df_standings["TEAM"] == selected_team]
        is_po = bool(row["PLAYOFF_TEAM"].iloc[0]) if not row.empty else False
        if not is_po:
            st.warning(f"{selected_team} did not make the playoffs in 2024-25 — no playoff player stats to display.")
            st.stop()

    st.markdown(f"### Team Stats — {selected_team}")
    st.markdown("## 📌 General Stats")

    # --- First row KPIs ---
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi(df, "PTS_PG", "Points per Game")
    with c2:
        render_kpi(df, "REB_PG", "Rebounds per Game")
    with c3:
        render_kpi(df, "AST_PG", "Assists per Game")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Second row KPIs ---
    c4, c5, c6 = st.columns(3)
    with c4:
        render_kpi(df, "STL_PG", "Steals per Game")
    with c5:
        render_kpi(df, "BLK_PG", "Blocks per Game")
    with c6:
        render_kpi(df, "TOV_PG", "Turnovers per Game")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    
    # --------------------------------
    # Full Team — Field Parameter Style
    # --------------------------------
    st.markdown("## 🗂 Full Team")

    # Default columns (only keep those that actually exist)
    default_cols = [c for c in ["TEAM", "PLAYER_NAME", "PTS_PG", "AST_PG", "REB_PG", "MIN_PG"] if c in df.columns]

    # Additional fields you can add on top of defaults
    additional_fields = [c for c in df.columns if c not in default_cols]

    # Multiselect with "Select All"
    multiselect_options = ["Select All"] + additional_fields
    selected_extra = st.multiselect(
        "Add columns to display",
        options=multiselect_options,
        default=[],
        key="team_full_fields"
    )

    # Expand "Select All"
    if "Select All" in selected_extra:
        selected_extra = additional_fields

    # Final column list to show
    cols_to_show = default_cols + selected_extra

    if cols_to_show:
        st.dataframe(df[cols_to_show], hide_index=True, use_container_width=True)
    else:
        st.info("No columns selected. Please choose at least one.")




# ===============================
# 💰 Salaries
# ===============================
with tab_salaries:
    st.markdown(f"### Player Salaries — {selected_team}")
    df_salaries_team = df_salaries[df_salaries["TEAM"] == selected_team]
    st.dataframe(df_salaries_team, hide_index=True, use_container_width=True)
