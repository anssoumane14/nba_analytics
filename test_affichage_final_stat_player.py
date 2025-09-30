import pandas as pd
import re
import streamlit as st
from stat_functions import (
    afficher_offensif,
    afficher_defensif,
    graphique_barres,
    pick_display_columns,
)
import plotly.express as px

st.set_page_config(layout="wide")

# -------------------------------
# Load Data
# -------------------------------
df_rs = pd.read_csv("flat_table/flat_rs_player_final_stats.csv", encoding="utf-8-sig")
df_po = pd.read_csv("flat_table/flat_po_player_final_stats.csv", encoding="utf-8-sig")
df_test = pd.read_csv("flat_table/flat_advanced_player.csv", encoding="utf-8-sig")




# -------------------------------
# Title
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>NBA Statistiques</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align: center; color: gray;'>Les chiffres derrière les performances</h3>", 
    unsafe_allow_html=True
)

# -------------------------------
# Tabs
# -------------------------------
tab_basic, tab_advanced = st.tabs(["📊 Statistiques de base", "📈 Analyses avancées"])

# ===============================
# I. BASIC STATISTICS
# ===============================
with tab_basic:
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1], gap="large")

    with col1:
        metric_filter = st.selectbox(
            "Choisir une vue", 
            ["Leaders", "Top 30", "Toutes les données"],
            key="metric_filter"
        )

    with col2:
        season_filter = st.radio(
            "Partie de la saison", 
            ["Saison régulière", "Playoffs"], 
            horizontal=True,
            key="season_filter"
        )

    with col3:
        df_temp = df_rs if season_filter == "Saison régulière" else df_po
        seasons = sorted(df_temp["SEASON"].unique(), reverse=True)
        season_choice = st.selectbox("Saison", seasons, key="season_choice")

    with col4:
        stat_mode = st.radio(
            "Mode statistique", 
            ["Par match", "Total"], 
            horizontal=True,
            key="stat_mode"
        )

    if metric_filter in ["Top 30", "Toutes les données"]:
        view_mode = "Tableau"
    else:
        with col5:
            view_mode = st.radio(
                "Mode d'affichage", 
                ["Tableau", "Diagramme en barres"], 
                horizontal=True,
                key="view_mode"
            )

    df = df_rs if season_filter == "Saison régulière" else df_po
    df = df[(df["SEASON"] == season_choice) & (df["G"] > 10) & (df["MP"] > 100)]

    if metric_filter == "Leaders":
        afficher_offensif(df, season_choice, stat_mode, view_mode)
        st.divider()
        afficher_defensif(df, season_choice, stat_mode, view_mode)

    elif metric_filter == "Top 30":
        stat_choice = st.selectbox(
            "Sélectionner une statistique",
            ["Points", "Passes décisives", "Rebonds totaux", "Rebonds offensifs",
             "Rebonds défensifs", "Minutes", "3 points marqués", "Lancers francs marqués",
             "Contres", "Interceptions", "Ballons perdus"]
        )
        stat_map = {
            "Points": "PTS",
            "Passes décisives": "AST",
            "Rebonds totaux": "TRB",
            "Rebonds offensifs": "ORB",
            "Rebonds défensifs": "DRB",
            "Minutes": "MP",
            "3 points marqués": "3P",
            "Lancers francs marqués": "FT",
            "Contres": "BLK",
            "Interceptions": "STL",
            "Ballons perdus": "TOV",
        }

        suffix = "_PG" if stat_mode == "Par match" else ""
        chosen_col = stat_map[stat_choice] + suffix

        top30 = df[["PLAYER", "TEAM", chosen_col]].sort_values(by=chosen_col, ascending=False).head(30)

        st.markdown(f"## Top 30 {stat_choice} ({stat_mode}) - {season_choice} ({season_filter})")
        st.dataframe(top30, hide_index=True, use_container_width=True)

    elif metric_filter == "Toutes les données":
        st.markdown(f"## {season_filter} — Données complètes ({season_choice})")

        cols = pick_display_columns(df, key="all_data_cols")
        st.dataframe(df[cols], hide_index=True, use_container_width=True)


# ===============================
# II. ADVANCED ANALYTICS
# ===============================

import re  # ✅ nécessaire pour clean_player_names

df_rs_adv = pd.read_csv("flat_table/flat_rs_player_final_stats.csv", encoding="utf-8-sig")
df_po_adv = pd.read_csv("flat_table/flat_po_player_final_stats.csv", encoding="utf-8-sig")
df_test_adv = pd.read_csv("flat_table/flat_advanced_player.csv", encoding="utf-8-sig")

# ✅ Normaliser SEASON (utile pour les PO au format YYYY)
for df_x in [df_rs_adv, df_po_adv]:
    df_x["SEASON"] = df_x["SEASON"].astype(str)
    df_x["SEASON"] = df_x["SEASON"].apply(
        lambda x: f"{int(x)-1}-{str(x)[-2:]}" if len(x) == 4 else x
    )

# 🔧 Nettoyer les noms des joueurs uniquement pour Advanced
def clean_player_names(df: pd.DataFrame) -> pd.DataFrame:
    if "PLAYER" in df.columns:
        df["PLAYER"] = df["PLAYER"].astype(str).apply(lambda x: re.sub(r"\*", "", x).strip())
    return df

df_rs_adv = clean_player_names(df_rs_adv)
df_po_adv = clean_player_names(df_po_adv)
df_test_adv = clean_player_names(df_test_adv)

with tab_advanced:
    st.markdown("### 📈 Analyses Avancées")

    col1, col2 = st.columns(2)
    with col1:
        player_choice = st.selectbox("Choisir un joueur", sorted(df_rs_adv["PLAYER"].unique()))
    with col2:
        season_choice = st.selectbox("Choisir une saison", sorted(df_rs_adv["SEASON"].unique(), reverse=True))

    rs_filtered = df_rs_adv[(df_rs_adv["PLAYER"] == player_choice) & (df_rs_adv["SEASON"] == season_choice)]
    po_filtered = df_po_adv[(df_po_adv["PLAYER"] == player_choice) & (df_po_adv["SEASON"] == season_choice)]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"📊 Saison régulière — {season_choice}")
        if rs_filtered.empty:
            st.warning("⚠️ Pas de données RS.")
        else:
            st.dataframe(rs_filtered, hide_index=True, use_container_width=True)

    with col2:
        st.subheader(f"🏆 Playoffs — {season_choice}")
        if po_filtered.empty:
            st.info("ℹ️ Pas de données PO.")
        else:
            st.dataframe(po_filtered, hide_index=True, use_container_width=True)

    # ✅ Jeu de données avancé complet
    st.markdown("### 📂 Jeu de données avancé (toutes les colonnes)")

    player_choice_adv = st.selectbox(
        "Choisir un joueur (dataset avancé)", 
        ["Tous"] + sorted(df_test_adv["PLAYER"].unique()),
        key="adv_player_filter"
    )

    if player_choice_adv != "Tous":
        df_display = df_test_adv[df_test_adv["PLAYER"] == player_choice_adv]
    else:
        df_display = df_test_adv

    st.dataframe(df_display, hide_index=True, use_container_width=True)
