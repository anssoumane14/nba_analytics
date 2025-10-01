# processed_data_pg.py

import os
import pandas as pd
import streamlit as st
from functions import compute_per_game

# ---------------------------
# Helpers
# ---------------------------
def load_concat(folder: str) -> pd.DataFrame:
    """Concatène tous les CSV d'un dossier"""
    if not os.path.exists(folder):
        return pd.DataFrame()
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    dfs = []
    for file in files:
        path = os.path.join(folder, file)
        try:
            df = pd.read_csv(path, encoding="utf-8-sig")
            dfs.append(df)
        except Exception as e:
            print(f"⚠️ erreur lecture {file}: {e}")
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def display_kpis(df):
    """Affiche les KPIs principaux après filtre (totaux + moyennes pondérées)"""
    if df.empty:
        st.info("⚠️ No data to display.")
        return

    total_pts = df["PTS"].sum() if "PTS" in df.columns else 0
    total_ast = df["AST"].sum() if "AST" in df.columns else 0
    total_trb = df["TRB"].sum() if "TRB" in df.columns else 0
    total_games = df["G"].sum() if "G" in df.columns else 0

    mean_pts = (total_pts / total_games) if total_pts and total_games else None
    mean_ast = (total_ast / total_games) if total_ast and total_games else None
    mean_trb = (total_trb / total_games) if total_trb and total_games else None

    st.markdown("### 📌 KPIs Résumés")
    cols = st.columns(4)
    cols[0].metric("Total PTS", f"{total_pts:.0f}" if total_pts else "N/A")
    cols[1].metric("Total AST", f"{total_ast:.0f}" if total_ast else "N/A")
    cols[2].metric("Total TRB", f"{total_trb:.0f}" if total_trb else "N/A")
    cols[3].metric("Total Games", f"{total_games:.0f}" if total_games else "N/A")

    cols = st.columns(3)
    cols[0].metric("PTS_PG (career avg)", f"{mean_pts:.1f}" if mean_pts else "N/A")
    cols[1].metric("AST_PG (career avg)", f"{mean_ast:.1f}" if mean_ast else "N/A")
    cols[2].metric("TRB_PG (career avg)", f"{mean_trb:.1f}" if mean_trb else "N/A")


def apply_filters(df):
    """Applique filtres globaux player + season"""
    if df.empty:
        return df
    df_f = df.copy()
    if selected_player != "All":
        if "Player" in df_f.columns:
            df_f = df_f[df_f["Player"] == selected_player]
        elif "PLAYER" in df_f.columns:
            df_f = df_f[df_f["PLAYER"] == selected_player]
    if selected_season != "All":
        if "Season" in df_f.columns:
            df_f = df_f[df_f["Season"] == selected_season]
        elif "SEASON" in df_f.columns:
            df_f = df_f[df_f["SEASON"] == selected_season]
    return df_f


# ---------------------------
# Main Streamlit App
# ---------------------------
st.set_page_config(layout="wide")
st.title("🏀 NBA Processed Data PG Viewer")

# Load datasets
df_pg_rs = load_concat("processed_data_pg/rs")
df_pg_po = load_concat("processed_data_pg/po")

# ---------------------------
# Global filters
# ---------------------------
all_players = pd.concat([
    df_pg_rs["PLAYER"] if "PLAYER" in df_pg_rs.columns else pd.Series(),
    df_pg_po["PLAYER"] if "PLAYER" in df_pg_po.columns else pd.Series()
], ignore_index=True).dropna().unique()

all_seasons = pd.concat([
    df_pg_rs["SEASON"] if "SEASON" in df_pg_rs.columns else pd.Series(),
    df_pg_po["SEASON"] if "SEASON" in df_pg_po.columns else pd.Series()
], ignore_index=True).dropna().unique()

col1, col2 = st.columns(2)
selected_player = col1.selectbox("🎯 Select Player", ["All"] + sorted(all_players))
selected_season = col2.selectbox("📅 Select Season", ["All"] + sorted(all_seasons))

season_type_choice = st.radio(
    "🏆 Select Season Type",
    ["Regular Season", "Playoffs"],
    horizontal=True
)

# ---------------------------
# Display
# ---------------------------
st.subheader(f"Processed Data PG — {season_type_choice}")
df_pg_filtered = apply_filters(df_pg_rs if season_type_choice == "Regular Season" else df_pg_po)
st.dataframe(df_pg_filtered, use_container_width=True)
display_kpis(df_pg_filtered)
