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

  # Nettoyer noms joueurs
def clean_player_names(df: pd.DataFrame) -> pd.DataFrame:
    if "PLAYER" in df.columns:
        df["PLAYER"] = df["PLAYER"].astype(str).apply(lambda x: re.sub(r"\*", "", x).strip())
    return df

st.set_page_config(layout="wide")

# -------------------------------
# Load Data
# -------------------------------
df_rs = pd.read_csv("flat_table/flat_rs_player.csv", encoding="utf-8-sig")
df_po = pd.read_csv("flat_table/flat_po_player.csv", encoding="utf-8-sig")

df_rs = clean_player_names(df_rs)
df_po = clean_player_names(df_po)

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
# II. ADVANCED ANALYTICS (RS vs PO bar chart)
# ===============================
with tab_advanced:
    st.markdown("### 📈 Analyses Avancées")
    
    df_rs = clean_player_names(df_rs)
    df_po = clean_player_names(df_po)

    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        player_choice = st.selectbox("Choisir un joueur", sorted(df_rs["PLAYER"].unique()))
    with col2:
        season_choice = st.selectbox("Choisir une saison", sorted(df_rs["SEASON"].unique(), reverse=True))

    # Sélection données
    rs_filtered = df_rs[(df_rs["PLAYER"] == player_choice) & (df_rs["SEASON"] == season_choice)]
    po_filtered = df_po[(df_po["PLAYER"] == player_choice) & (df_po["SEASON"] == season_choice)]

    st.subheader(f"📊 Comparaison RS vs PO — {player_choice}, {season_choice}")

    if rs_filtered.empty:
        st.warning("⚠️ Pas de données RS.")
    else:
        rs_row = rs_filtered.iloc[0]

        if not po_filtered.empty:
            po_row = po_filtered.iloc[0]

            # Stats comparées
            base_metrics = {
                "Points": "PTS_PG",
                "Passes décisives": "AST_PG",
                "Rebonds": "TRB_PG",
                "Interceptions": "STL_PG",
                "Contres": "BLK_PG",
                "Minutes": "MP_PG",
            }

            data = []
            for label, col in base_metrics.items():
                if col in rs_row and col in po_row:
                    rs_val = rs_row[col]
                    po_val = po_row[col]
                    diff = po_val - rs_val
                    data.append([label, rs_val, po_val, diff])

            df_diff = pd.DataFrame(data, columns=["Stat", "RS", "PO", "Différentiel"])
            #st.dataframe(df_diff, hide_index=True, use_container_width=True)

            fig_bar = px.bar(
                df_diff.melt(id_vars="Stat", value_vars=["RS", "PO"], var_name="Contexte", value_name="Valeur"),
                x="Stat", y="Valeur", color="Contexte", barmode="group",
                text="Valeur"
            )

            fig_bar.update_traces(textposition="outside")  # ✅ met les valeurs en dehors des barres

            fig_bar.update_layout(
                title=dict(
                    text=f"{player_choice} — RS vs PO ({season_choice})",
                    font=dict(color="white")  # 👻 Titre "invisible"
                ),
                yaxis=dict(visible=False),
                xaxis=dict(title=None),
                plot_bgcolor="white",
                margin=dict(t=80, b=40, l=20, r=20),  # ✅ marges personnalisées
                height=500  # ✅ agrandir un peu la figure
            )

            st.plotly_chart(fig_bar, use_container_width=True)

             


        else:
            st.info(f"ℹ️ {player_choice} n'a pas de stats en playoffs pour la saison {season_choice}.")
            st.dataframe(rs_filtered, hide_index=True, use_container_width=True)
