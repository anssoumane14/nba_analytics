# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import plotly.express as px

from nav_bar import show_navbar
from stat_functions import render_kpi, pick_display_columns, render_kpi_box
from functions import map_team_names

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
# Load Data
# -------------------------------
df_salaries_raw = load_flat("flat_salaries_2026")
df_rs_raw       = load_flat("flat_rs_player")

# -------------------------------
# Title
# -------------------------------
st.markdown(f"<h1 style='text-align: center;'>NBA Team Overview</h1>", unsafe_allow_html=True)

# -------------------------------
# Season Selector
# -------------------------------
all_seasons = set()
if "SEASON" in df_rs_raw.columns:
    all_seasons.update(df_rs_raw["SEASON"].dropna().unique())

season_filter = None
if all_seasons:
    season_filter = st.selectbox("Select a Season", sorted(all_seasons, reverse=True))

# -------------------------------
# Step 1. Clean salaries
# -------------------------------
if not df_salaries_raw.empty:
    if df_salaries_raw.columns[-1] == "-9999":
        df_salaries_raw = df_salaries_raw.iloc[:, :-1]

    df_salaries = df_salaries_raw.rename(columns={"Player": "PLAYER", "Tm": "TEAM"})
    df_salaries = map_team_names(df_salaries, abbr_col="TEAM")

    year_cols = [
        c for c in df_salaries.columns
        if c not in ["PLAYER", "TEAM", "Guaranteed"] and not c.startswith("Rk")
    ]

    for col in year_cols:
        df_salaries[col] = (
            df_salaries[col]
            .astype(str)
            .str.replace(r"[^0-9]", "", regex=True)
            .replace("", "0")
            .astype(int)
        )

    df_salaries_long = df_salaries.melt(
        id_vars=["PLAYER", "TEAM", "Guaranteed"],
        value_vars=year_cols,
        var_name="YEAR",
        value_name="SALARY_NUM"
    )

# -------------------------------
# Step 2. Clean df_rs (keep last team only)
# -------------------------------
def keep_last_team(team_str: str) -> str:
    if pd.isna(team_str):
        return None
    return str(team_str).split("/")[-1].strip()

df_rs = df_rs_raw.copy()
if not df_rs.empty:
    df_rs["TEAM"] = df_rs["TEAM"].apply(keep_last_team)
    if "POS" in df_rs.columns:
        df_rs = df_rs.rename(columns={"POS": "POSITION"})

# -------------------------------
# Step 3. Merge salaries + stats
# -------------------------------
if not df_salaries_raw.empty and not df_rs.empty:
    df_join = pd.merge(
        df_salaries_long,
        df_rs[["PLAYER", "SEASON", "POSITION"]],
        on="PLAYER",
        how="left"
    )

    # -------------------------------
    # Step 4. Filters
    # -------------------------------
    all_teams = sorted(df_join["TEAM"].dropna().unique())
    selected_team = st.selectbox("Select a Team", all_teams, index=0)

    df_team = df_join[df_join["TEAM"] == selected_team]

    all_years = sorted(df_team["YEAR"].dropna().unique())
    selected_year = st.selectbox("Select a Year", all_years, index=0)

    df_team_year = df_team[df_team["YEAR"] == selected_year].copy()

    # ⚡ Rule: keep only the most recent season per player
    df_team_year = (
        df_team_year.sort_values(by="SEASON", ascending=False)
        .drop_duplicates(subset=["PLAYER"], keep="first")
    )

    # -------------------------------
    # Step 5. KPIs
    # -------------------------------
    team_total = int(df_team_year["SALARY_NUM"].sum()) if not df_team_year.empty else 0
    if not df_team_year.empty and df_team_year["SALARY_NUM"].max() > 0:
        top_row = df_team_year.loc[df_team_year["SALARY_NUM"].idxmax()]
        top_player = str(top_row["PLAYER"])
        top_salary = int(top_row["SALARY_NUM"])
    else:
        top_player, top_salary = "—", 0

    c1, c2 = st.columns(2)
    with c1: render_kpi_box("Team Payroll", f"${team_total:,.0f}", f"{selected_team} — {selected_year}")
    with c2: render_kpi_box("Top Paid Player", f"${top_salary:,.0f}", top_player)

    # -------------------------------
    # Step 6. Pie Chart
    # -------------------------------
    df_pie = (
        df_team_year.groupby("POSITION", as_index=False)["SALARY_NUM"]
        .sum()
        .sort_values("SALARY_NUM", ascending=False)
    )

    if df_pie.empty or df_pie["SALARY_NUM"].sum() == 0:
        st.info("No salary data available for this team/year.")
    else:
        fig = px.pie(
            df_pie,
            names="POSITION",
            values="SALARY_NUM",
            title=f"Salaries by Position — {selected_team} ({selected_year})",
            hole=0.35,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>$%{value:,.0f} (%{percent:.1%})",
            hovertemplate="%{label}<br>Total: $%{value:,.0f}<br>%{percent}"
        )
        fig.update_layout(margin=dict(t=60, b=30, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Step 7. Table
    # -------------------------------
    st.markdown(f"### Salaries Table — {selected_team} ({selected_year})")
    st.dataframe(
        df_team_year[["PLAYER", "TEAM", "POSITION", "SEASON", "YEAR", "SALARY_NUM"]],
        hide_index=True,
        use_container_width=True
    )
