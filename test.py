import pandas as pd
import streamlit as st
import plotly.express as px
from stat_functions import pick_display_columns, afficher_offensif, afficher_defensif

# -------------------------------
# Config
# -------------------------------
st.set_page_config(layout="wide")

# -------------------------------
# Charger les données (CSV plats)
# -------------------------------
df_rs = pd.read_csv("processed_data/flat_rs.csv", encoding="utf-8-sig")
df_po = pd.read_csv("processed_data/flat_po.csv", encoding="utf-8-sig")

# -------------------------------
# Titre principal
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>📊 Statistiques NBA</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align: center; color: gray;'>Les chiffres derrière les performances (1976 - 2025)</h3>", 
    unsafe_allow_html=True
)

# -------------------------------
# Tabs
# -------------------------------
tab_basics, tab_advanced = st.tabs(["📊 Statistiques de Base", "📈 Analyses Avancées"])


# filtre : les joueurs qui ont ete trade on garde que leur dernier team example luka

# ===============================
# I. BASIC STATS
# ===============================
with tab_basics:
    # -------------------------------
    # Filtres
    # -------------------------------
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1], gap="large")

    with col1:
        season = st.selectbox("Saison", sorted(df_rs["SEASON"].unique(), reverse=True))

    with col2:
        season_filter = st.radio(
            "Partie de la saison", 
            ["Saison régulière", "Playoffs"], 
            horizontal=True,
            key="season_filter"
        )

    with col3:
        stat_mode = st.radio(
            "Mode statistique", 
            ["Par match", "Total"], 
            horizontal=True,
            key="stat_mode"
        )

    with col4:
        metric_filter = st.selectbox(
            "Choisir une vue", 
            ["Leaders", "Top 30", "Toutes les données"],
            key="metric_filter"
        )

    # Affichage conditionnel du mode d'affichage
    if metric_filter in ["Top 30", "Toutes les données"]:
        view_mode = "Tableau"  # forcé en tableau
    else:
        with col5:
            view_mode = st.radio(
                "Mode d'affichage", 
                ["Tableau", "Diagramme en barres"], 
                horizontal=True,
                key="view_mode"
            )

    # -------------------------------
    # Sélection du dataset
    # -------------------------------
    df = df_rs if season_filter == "Saison régulière" else df_po
    df = df[df["SEASON"] == season]

    # -------------------------------
    # Affichage selon les filtres
    # -------------------------------
    if metric_filter == "Leaders":
        afficher_offensif(df, season_filter, stat_mode, view_mode)
        st.divider()
        afficher_defensif(df, season_filter, stat_mode, view_mode)

    elif metric_filter == "Top 30":
        stat_choice = st.selectbox(
            "Sélectionner une statistique",
            [
                "Points",
                "Passes décisives",
                "Rebonds totaux",
                "Rebonds défensifs",
                "Minutes",
                "3 points marqués",
                "Lancers francs marqués",
                "Contres",
                "Interceptions",
                "Ballons perdus",
            ]
        )
        suffix = "_PG" if stat_mode == "Par match" else ""
        stat_map = {
            "Points": "PTS",
            "Passes décisives": "AST",
            "Rebonds totaux": "TRB",
            "Rebonds défensifs": "DRB",
            "Minutes": "MP",
            "3 points marqués": "3P",
            "Lancers francs marqués": "FT",
            "Contres": "BLK",
            "Interceptions": "STL",
            "Ballons perdus": "TOV",
        }

        chosen_col = stat_map[stat_choice] + suffix
        top30 = (
            df[["PLAYER", "TEAM", chosen_col]]
            .sort_values(by=chosen_col, ascending=False)
            .head(30)
        )

        st.markdown(f"##  Top 30 {stat_choice} ({stat_mode}) - {season_filter}")
        st.dataframe(top30, hide_index=True, use_container_width=True)

    elif metric_filter == "Toutes les données":
        st.markdown(f"##  {season_filter} — Données complètes (par champ)")

        cols_to_show = pick_display_columns(
            df,
            base_cols=("TEAM", "PLAYER", "PTS_PG", "AST_PG", "TRB_PG", "MP_PG"),
            exclude=("PLAYER_ID", "RK"),
            key="all_data_fields"
        )

        if cols_to_show:
            st.dataframe(df[cols_to_show], hide_index=True, use_container_width=True)
        else:
            st.info("Aucune colonne sélectionnée. Veuillez en choisir au moins une.")

# ===============================
# II. ADVANCED ANALYTICS
# ===============================
with tab_advanced:
    st.markdown("### 📈 Analyses Avancées")
