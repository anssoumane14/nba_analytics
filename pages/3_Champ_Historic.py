# -*- coding: utf-8 -*-
import unicodedata
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="NBA History", layout="wide")
from nav_bar import show_navbar

# -------------------------------
# Navigation bar
# -------------------------------
show_navbar()

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")

    # Drop empty column if exists
    if "UNNAMED:_5" in df.columns:
        df = df.drop(columns=["UNNAMED:_5"])

    # Standardize col names
    df.columns = [c.strip().replace(" ", "_").upper() for c in df.columns]

    # Normalize naming
    if "RUNNER-UP" in df.columns:
        df = df.rename(columns={"RUNNER-UP": "RUNNER"})
    if "YEAR" in df.columns:
        df["YEAR"] = df["YEAR"].astype(str)

    return df

df_raw = load_data("flat_table/flat_champ_2025.csv")

# -------------------------------
# Normalize text
# -------------------------------
def normalize_txt(s: str) -> str:
    if pd.isna(s):
        return ""
    s = str(s).strip().casefold()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s

# -------------------------------
# Normalized columns
# -------------------------------
df = df_raw.copy()
for col in ["CHAMPION", "RUNNER", "FINALS_MVP", "POINTS", "REBOUNDS", "ASSISTS"]:
    if col in df.columns:
        df[f"{col}_NORM"] = df[col].map(normalize_txt)

# Build player search column
df["PLAYERS_ALL_NORM"] = (
    df.get("FINALS_MVP_NORM", pd.Series("", index=df.index)).fillna("") + "|" +
    df.get("POINTS_NORM", pd.Series("", index=df.index)).fillna("") + "|" +
    df.get("REBOUNDS_NORM", pd.Series("", index=df.index)).fillna("") + "|" +
    df.get("ASSISTS_NORM", pd.Series("", index=df.index)).fillna("")
)

# -------------------------------
# Split into 2 dataframes
# -------------------------------
df_champ = df[["YEAR", "LG", "CHAMPION", "RUNNER", "FINALS_MVP"]].copy()
df_stats = df[["YEAR", "POINTS", "REBOUNDS", "ASSISTS", "WIN_SHARES"]].copy()

# -------------------------------
# Filters
# -------------------------------
years = ["All"] + sorted(df["YEAR"].dropna().unique().tolist(), reverse=True)
champs = ["All"] + sorted(df["CHAMPION"].dropna().unique().tolist())
runners = ["All"] + sorted(df["RUNNER"].dropna().unique().tolist())
players = ["All"] + sorted(
    pd.concat([
        df["FINALS_MVP"].dropna(),
        df["POINTS"].dropna(),
        df["REBOUNDS"].dropna(),
        df["ASSISTS"].dropna(),
    ]).astype(str).unique().tolist()
)

c1, c2, c3, c4 = st.columns(4)
year_filter = c1.selectbox("Select Year", years)
champ_filter = c2.selectbox("Select Champion", champs)
runner_filter = c3.selectbox("Select Runner-Up", runners)
player_filter = c4.selectbox("Select Player", players)

# Apply filters
filtered = df.copy()
if year_filter != "All":
    filtered = filtered[filtered["YEAR"] == year_filter]
if champ_filter != "All":
    filtered = filtered[filtered["CHAMPION"] == champ_filter]
if runner_filter != "All":
    filtered = filtered[filtered["RUNNER"] == runner_filter]
if player_filter != "All":
    norm_p = normalize_txt(player_filter)
    filtered = filtered[
        filtered["PLAYERS_ALL_NORM"].str.split("|").apply(lambda lst: norm_p in lst)
    ]

# Filter sub-dataframes
df_champ_filtered = df_champ[df_champ["YEAR"].isin(filtered["YEAR"])]
df_stats_filtered = df_stats[df_stats["YEAR"].isin(filtered["YEAR"])]

# -------------------------------
# Display
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Finals Summary")
    if df_champ_filtered.empty:
        st.info("No results.")
    else:
        st.dataframe(df_champ_filtered, hide_index=True, use_container_width=True)

with col2:
    st.markdown("### Playoff Performances")
    if df_stats_filtered.empty:
        st.info("No results.")
    else:
        st.dataframe(df_stats_filtered, hide_index=True, use_container_width=True)
