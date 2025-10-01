# pipeline_viewer.py

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
    """Affiche les KPIs principaux après filtre"""
    if df.empty:
        return

    total_pts = df["PTS"].sum() if "PTS" in df.columns else None
    total_ast = df["AST"].sum() if "AST" in df.columns else None
    total_trb = df["TRB"].sum() if "TRB" in df.columns else None
    total_games = df["G"].sum() if "G" in df.columns else None

    mean_pts = df["PTS_PG"].mean() if "PTS_PG" in df.columns else None
    mean_ast = df["AST_PG"].mean() if "AST_PG" in df.columns else None
    mean_trb = df["TRB_PG"].mean() if "TRB_PG" in df.columns else None

    st.markdown("### 📌 KPIs Résumés")
    cols = st.columns(4)
    cols[0].metric("Total PTS", f"{total_pts:.0f}" if total_pts else "N/A")
    cols[1].metric("Total AST", f"{total_ast:.0f}" if total_ast else "N/A")
    cols[2].metric("Total TRB", f"{total_trb:.0f}" if total_trb else "N/A")
    cols[3].metric("Total Games", f"{total_games:.0f}" if total_games else "N/A")

    cols = st.columns(3)
    cols[0].metric("PTS_PG (avg)", f"{mean_pts:.1f}" if mean_pts else "N/A")
    cols[1].metric("AST_PG (avg)", f"{mean_ast:.1f}" if mean_ast else "N/A")
    cols[2].metric("TRB_PG (avg)", f"{mean_trb:.1f}" if mean_trb else "N/A")

# ---------------------------
# Main Streamlit App
# ---------------------------
st.set_page_config(layout="wide")
st.title("🏀 NBA Pipeline Viewer")

# Load all datasets
df_raw_rs = load_concat("raw_data/rs")
df_raw_po = load_concat("raw_data/po")

df_proc_rs = load_concat("processed_data/rs")
df_proc_po = load_concat("processed_data/po")

df_pg_rs = load_concat("processed_data_pg/rs")
df_pg_po = load_concat("processed_data_pg/po")

# ---------------------------
# Global filters
# ---------------------------
all_players = pd.concat([
    df_raw_rs["Player"] if "Player" in df_raw_rs.columns else pd.Series(),
    df_raw_po["Player"] if "Player" in df_raw_po.columns else pd.Series(),
    df_proc_rs["PLAYER"] if "PLAYER" in df_proc_rs.columns else pd.Series(),
    df_pg_rs["PLAYER"] if "PLAYER" in df_pg_rs.columns else pd.Series()
], ignore_index=True).dropna().unique()

all_seasons = pd.concat([
    df_raw_rs["Season"] if "Season" in df_raw_rs.columns else pd.Series(),
    df_raw_po["Season"] if "Season" in df_raw_po.columns else pd.Series(),
    df_proc_rs["SEASON"] if "SEASON" in df_proc_rs.columns else pd.Series(),
    df_pg_rs["SEASON"] if "SEASON" in df_pg_rs.columns else pd.Series()
], ignore_index=True).dropna().unique()

col1, col2, col3 = st.columns(3)
selected_player = col1.selectbox("🎯 Select Player", ["All"] + sorted(all_players))
selected_season = col2.selectbox("📅 Select Season", ["All"] + sorted(all_seasons))
selected_type = col3.selectbox("🏆 Select Season Type", ["All", "Regular Season", "Playoffs"])

# ---------------------------
# Display by stage
# ---------------------------
tab1, tab2, tab3 = st.tabs(["Raw Data", "Processed Data", "Processed Data PG"])

def apply_filters(df):
    """Applique filtres globaux player + season + season type"""
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
    if selected_type != "All":
        if "Season_Type" in df_f.columns:
            df_f = df_f[df_f["Season_Type"] == selected_type]
        elif "SEASON_TYPE" in df_f.columns:
            df_f = df_f[df_f["SEASON_TYPE"] == selected_type]
    return df_f

with tab1:
    st.subheader("Raw Data (RS + PO)")
    df_raw_filtered = pd.concat([
        apply_filters(df_raw_rs),
        apply_filters(df_raw_po)
    ], ignore_index=True)
    st.dataframe(df_raw_filtered, use_container_width=True)
    display_kpis(df_raw_filtered)

with tab2:
    st.subheader("Processed Data (RS + PO)")
    df_proc_filtered = pd.concat([
        apply_filters(df_proc_rs),
        apply_filters(df_proc_po)
    ], ignore_index=True)
    st.dataframe(df_proc_filtered, use_container_width=True)
    display_kpis(df_proc_filtered)

with tab3:
    st.subheader("Processed Data PG (RS + PO)")
    df_pg_filtered = pd.concat([
        apply_filters(df_pg_rs),
        apply_filters(df_pg_po)
    ], ignore_index=True)
    st.dataframe(df_pg_filtered, use_container_width=True)
    display_kpis(df_pg_filtered)
