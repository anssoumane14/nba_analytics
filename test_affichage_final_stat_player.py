# view_players.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="NBA Players Data", layout="wide")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    df_rs_stats = pd.read_csv("flat_table/flat_rs_player_final_stats.csv", encoding="utf-8-sig")
    df_po_stats = pd.read_csv("flat_table/flat_po_player_final_stats.csv", encoding="utf-8-sig")
    df_rs = pd.read_csv("flat_table/flat_rs_player_final.csv", encoding="utf-8-sig")
    df_po = pd.read_csv("flat_table/flat_po_player_final.csv", encoding="utf-8-sig")

    # ✅ Always recompute SEASON_YEAR when loading
    for df in [df_rs, df_po, df_rs_stats, df_po_stats]:
        if "SEASON" in df.columns:
            df["SEASON_YEAR"] = df["SEASON"].astype(str).str.split("-").str[0].astype(int) + 1

    return df_rs, df_po, df_rs_stats, df_po_stats

df_rs, df_po, df_rs_stats, df_po_stats = load_data()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("🔎 Filtres")

season_filter = st.sidebar.selectbox(
    "Partie de la saison", ["Saison régulière", "Playoffs"], index=0
)

if season_filter == "Saison régulière":
    df_raw = df_rs
    df_stats = df_rs_stats
else:
    df_raw = df_po
    df_stats = df_po_stats

# Filter by season year
season_years = sorted(df_raw["SEASON_YEAR"].unique(), reverse=True)
season_year = st.sidebar.selectbox("Choisir une année de saison", season_years)

df_raw_season = df_raw[df_raw["SEASON_YEAR"] == season_year]
df_stats_season = df_stats[df_stats["SEASON_YEAR"] == season_year]

# Player filter
players = sorted(df_raw_season["PLAYER"].unique())
player = st.sidebar.selectbox("Choisir un joueur", ["Tous"] + players)

if player != "Tous":
    df_raw_season = df_raw_season[df_raw_season["PLAYER"] == player]
    df_stats_season = df_stats_season[df_stats_season["PLAYER"] == player]

# -------------------------------
# Main Display
# -------------------------------
st.title("🏀 NBA Player Stats Explorer")

for name, df in {
    "RS Raw": df_rs,
    "PO Raw": df_po,
    "RS Final Stats": df_rs_stats,
    "PO Final Stats": df_po_stats
}.items():
    st.subheader(f"📑 {name} Columns")
    st.write(df.columns.tolist())

st.markdown(
    f"### {season_filter} — Saison {season_year}-{str(season_year+1)[-2:]}"
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📂 Raw Processed Data")
    st.dataframe(df_raw_season, hide_index=True, use_container_width=True)

with col2:
    st.subheader("✅ Final Stats Data (Cleaned)")
    st.dataframe(df_stats_season, hide_index=True, use_container_width=True)
