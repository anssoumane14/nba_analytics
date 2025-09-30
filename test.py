import pandas as pd
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


# -------------------------------
# Filter game and mintutes
# revoir les teams : NJN = unknown = raw layer + team maping
# -------------------------------

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
    # Filters
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

    # ✅ NEW : filtre par saison
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

    # Force table mode if needed
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

    # Select dataset with filters
    df = df_rs if season_filter == "Saison régulière" else df_po
    df = df[(df["SEASON"] == season_choice) & (df["G"] > 10) & (df["MP"] > 100)]

    # Affichage conditionnel
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
with tab_advanced:
    st.markdown("### 📈 Analyses Avancées")

    col1, col2 = st.columns(2)
    with col1:
        season = st.selectbox("Choisir une saison", sorted(df_rs["SEASON"].unique(), reverse=True))
    with col2:
        player = st.selectbox("Choisir un joueur", sorted(df_rs["PLAYER"].unique()))

    rs_stats = df_rs[(df_rs["SEASON"] == season) & (df_rs["PLAYER"] == player)]
    po_stats = df_po[(df_po["SEASON"] == season) & (df_po["PLAYER"] == player)]

    if rs_stats.empty or po_stats.empty:
        st.warning("⚠️ Données incomplètes pour ce joueur/saison (pas de RS ou PO).")
    else:
        rs_row = rs_stats.iloc[0]
        po_row = po_stats.iloc[0]

        metrics = {
            "Points": "PTS_PG",
            "Passes décisives": "AST_PG",
            "Rebonds": "TRB_PG",
            "Interceptions": "STL_PG",
            "Contres": "BLK_PG",
            "Minutes": "MP_PG",
        }

        data = []
        for label, col in metrics.items():
            rs_val = rs_row[col]
            po_val = po_row[col]
            diff = po_val - rs_val
            data.append([label, rs_val, po_val, diff])

        df_diff = pd.DataFrame(data, columns=["Stat", "RS", "PO", "Différentiel"])

        st.markdown(f"#### 📊 {player} — Saison {season} (RS vs PO)")
        st.dataframe(df_diff, hide_index=True, use_container_width=True)

        st.markdown("#### 📉 Comparaison RS vs PO")
        fig_bar = px.bar(
            df_diff.melt(id_vars="Stat", value_vars=["RS", "PO"], var_name="Contexte", value_name="Valeur"),
            x="Stat", y="Valeur", color="Contexte", barmode="group",
            text="Valeur", title=f"{player} — RS vs PO"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("#### 🕸️ Profil Radar (RS vs PO)")
        fig_radar = px.line_polar(
            df_diff.melt(id_vars="Stat", value_vars=["RS", "PO"], var_name="Contexte", value_name="Valeur"),
            r="Valeur", theta="Stat", color="Contexte", line_close=True
        )
        st.plotly_chart(fig_radar, use_container_width=True)
