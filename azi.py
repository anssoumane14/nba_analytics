import os
import pandas as pd
import streamlit as st
from stat_functions import display_awards_kpi

FLAT_BASE = "flat_table"

# -------------------------------
# Helper pour charger
# -------------------------------
def load_flat(name: str) -> pd.DataFrame:
    path = f"{FLAT_BASE}/{name}.csv"
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")

# -------------------------------
# Charger toutes les tables
# -------------------------------
flats = {
    # Players
    "flat_rs_player": load_flat("flat_rs_player"),
    "flat_po_player": load_flat("flat_po_player"),
    "flat_advanced_player": load_flat("flat_advanced_player"),
    "flat_per_poss_player": load_flat("flat_per_poss_player"),
    "flat_pbp_player": load_flat("flat_pbp_player"),
    # Teams
    "flat_east_standing": load_flat("flat_east_standing"),
    "flat_west_standing": load_flat("flat_west_standing"),
    "flat_team_tot_stats": load_flat("flat_team_tot_stats"),
    "flat_team_pg_stats": load_flat("flat_team_pg_stats"),
    "flat_team_per_poss_stats": load_flat("flat_team_per_poss_stats"),
    "flat_team_adv_stats": load_flat("flat_team_adv_stats"),
    # Honors
    "flat_all_nba_teams": load_flat("flat_all_nba_teams"),
    "flat_all_def_teams": load_flat("flat_all_def_teams"),
    "flat_all_rookie_teams": load_flat("flat_all_rookie_teams"),
    # Awards
    "flat_awards": load_flat("flat_awards"),
}

# -------------------------------
# UI Streamlit
# -------------------------------
st.set_page_config(layout="wide")
st.title("🏀 NBA Flat Tables Explorer")

# Récupérer toutes les saisons disponibles
all_seasons = set()
for df in flats.values():
    if "SEASON" in df.columns:
        all_seasons.update(df["SEASON"].dropna().unique())

if all_seasons:
    season_filter = st.selectbox("🔎 Sélectionner une saison", sorted(all_seasons, reverse=True))
else:
    season_filter = None
    st.warning("⚠️ Aucune saison trouvée dans les flat tables")

# Résumé
st.subheader("📊 Résumé des tables")
summary = []
for name, df in flats.items():
    if df.empty:
        summary.append([name, 0, "⚠️ vide"])
    else:
        summary.append([name, len(df), "✅ ok"])
df_summary = pd.DataFrame(summary, columns=["Table", "Rows", "Status"])
st.dataframe(df_summary, hide_index=True, use_container_width=True)

# Tabs
tab_players, tab_teams, tab_honors, tab_awards = st.tabs(["👤 Players", "🏟️ Teams", "🏆 Honors", "🎖️ Awards"])

# -------------------------------
# Players
# -------------------------------
with tab_players:
    for name in ["flat_rs_player", "flat_po_player", "flat_advanced_player", "flat_per_poss_player", "flat_pbp_player"]:
        df = flats[name]
        st.markdown(f"### {name}")
        if not df.empty:
            if season_filter and "SEASON" in df.columns:
                df = df[df["SEASON"] == season_filter]
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info(f"{name} vide")

# -------------------------------
# Teams
# -------------------------------
with tab_teams:
    for name in ["flat_east_standing", "flat_west_standing", "flat_team_tot_stats", 
                 "flat_team_pg_stats", "flat_team_per_poss_stats", "flat_team_adv_stats"]:
        df = flats[name]
        st.markdown(f"### {name}")
        if not df.empty:
            if season_filter and "SEASON" in df.columns:
                df = df[df["SEASON"] == season_filter]
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info(f"{name} vide")

# -------------------------------
# Honors
# -------------------------------
with tab_honors:
    st.markdown("## 🏆 Awards KPI")
    display_awards_kpi(flats["flat_awards"], season_filter)
    for name in ["flat_all_nba_teams", "flat_all_def_teams", "flat_all_rookie_teams"]:
        df = flats[name]
        st.markdown(f"### {name}")
        if not df.empty:
            if season_filter and "SEASON" in df.columns:
                df = df[df["SEASON"] == season_filter]
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info(f"{name} vide")

# -------------------------------
# Awards
# -------------------------------
with tab_awards:
    df = flats["flat_awards"]
    st.markdown("### flat_awards")
    if not df.empty:
        if season_filter and "SEASON" in df.columns:
            df = df[df["SEASON"] == season_filter]
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.info("flat_awards vide")
