# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
import plotly.express as px

# Exécuter avec : py -m streamlit run pages/2_Statistics.py
# -------------------------------
# Configuration de la Page
# -------------------------------
st.set_page_config(layout="wide") # Configure la mise en page de la page Streamlit en mode large

# -------------------------------
# Affichage de la Barre de Navigation
# -------------------------------
# --- Barre de navigation supérieure (officielle) ---
c1, c2, c3, c4,c5 = st.columns(5) # Crée 5 colonnes pour les liens de navigation
with c1: st.page_link("home.py",                   label=" Accueil") # Lien vers la page d'accueil
with c2: st.page_link("pages/1_Team.py",           label=" Équipe") # Lien vers la page d'équipe
with c3: st.page_link("pages/2_Statistics.py",     label=" Statistiques") # Lien vers la page de statistiques
with c4: st.page_link("pages/3_Champ_Historic.py", label=" Historique") # Lien vers la page historique des champions
with c5: st.page_link("pages/4_Trade_Machine.py",  label=" Machine à Trade") # Lien vers la machine à trade

# -------------------------------
# Cache: chargement des données
# -------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def load_stats_data():
    df_reg = pd.read_excel("data/df_reg_season_players_filtered.xlsx")
    df_po  = pd.read_excel("data/df_playoff_players_filtered.xlsx")
    return df_reg, df_po

df_reg_season_players, df_playoff_players = load_stats_data()


# -------------------------------
# Titre de la Page
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>Statistiques NBA 2024-25</h1>", # Titre principal de la page
    unsafe_allow_html=True # Permet l'interprétation du HTML
)
st.markdown(
    "<h3 style='text-align: center; color: gray;'>Les Chiffres Derrière les Faits Saillants</h3>", # Sous-titre
    unsafe_allow_html=True # Permet l'interprétation du HTML
)

# -------------------------------
# Filtres d'Affichage (sur une seule ligne)
# -------------------------------
col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="large") # Crée 4 colonnes pour les filtres

with col1:
    # Sélecteur de mode d'affichage des statistiques (Leaders, Top 30, Données Complètes)
    metric_filter = st.selectbox(
        "Choisir une vue",
        ["Leaders", "Top 30", "Données Complètes"],
        key="metric_filter" # Clé unique pour ce widget
    )

with col2:
    # Sélecteur du type de saison (Saison Régulière ou Playoffs)
    season_filter = st.radio(
        "Type de Saison",
        ["Saison Régulière", "Playoffs"],
        horizontal=True, # Affiche les options horizontalement
        key="season_filter" # Clé unique pour ce widget
    )
with col3:
    # Sélecteur du mode statistique (Par Match ou Total)
    stat_mode = st.radio(
        "Mode Statistique",
        ["Par Match", "Total"],
        horizontal=True, # Affiche les options horizontalement
        key="stat_mode" # Clé unique pour ce widget
    )

# Affichage conditionnel du mode d'affichage (Tableau ou Diagramme en barres)
if metric_filter in ["Top 30", "Données Complètes"]:
    view_mode = "Table"  # Force l'affichage en mode Tableau pour "Top 30" et "Données Complètes"
else:
    with col4:
        view_mode = st.radio(
            "Mode d'Affichage",
            ["Tableau", "Diagramme en Barres"],
            horizontal=True, # Affiche les options horizontalement
            key="view_mode" # Clé unique pour ce widget
        )


# -------------------------------
# Sélection du Jeu de Données Approprié
# -------------------------------
# Sélectionne le DataFrame en fonction du filtre de saison (Saison Régulière ou Playoffs)
df = df_reg_season_players if season_filter == "Saison Régulière" else df_playoff_players

# Filtre les joueurs pour ne conserver que ceux ayant joué plus de 10 matchs (GP)
# et plus de 10 minutes par match (MIN_PG).
df = df[(df["GP"] > 10) & (df["MIN_PG"] > 10)]

import matplotlib.pyplot as plt

def custom_bar_chart(data, col_name, title):
    # Trier les données
    data_sorted = data.sort_values(by=col_name, ascending=True)  # ascending=True pour affichage du haut vers le bas
    
    fig, ax = plt.subplots(figsize=(8, 0.6 * len(data_sorted) + 2))

    # Tracer les barres
    bars = ax.barh(data_sorted["PLAYER_NAME"], data_sorted[col_name], color="skyblue", edgecolor="black")

    # Ajouter les valeurs au bout des barres
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5,               # un petit décalage
                bar.get_y() + bar.get_height()/2,
                f"{width:.1f}",
                va="center", ha="left", fontsize=10)

    # Enlever l’axe X
    ax.xaxis.set_visible(False)

    # Ajouter un titre
    ax.set_title(title, fontsize=14)

    # Fond blanc
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    plt.tight_layout()
    return fig



# -------------------------------
# Fonctions d'Affichage des Statistiques
# -------------------------------
def show_offense(df, label, mode, view_mode):
    """
    Affiche les statistiques offensives des joueurs.
    """
    suffix = "_PG" if mode == "Par Match" else "" # Ajoute '_PG' si le mode est 'Par Match'
    st.markdown(f"##  Statistiques Offensives ({label} - {mode})") # Titre de la section

    stats = {
        "Points": "PTS",
        "Passes Décisives": "AST",
        "Tirs à 3 Points Réussis": "FG3M",
        "Lancers Francs Réussis": "FTM"
    } # Dictionnaire des statistiques offensives à afficher

    col1, col2 = st.columns(2) # Crée 2 colonnes pour l'affichage des statistiques
    # Itère sur les statistiques et les colonnes pour les afficher
    for (title, col_name), col in zip(stats.items(), [col1, col2, col1, col2]):
        # Récupère les 5 meilleurs joueurs pour la statistique actuelle
        top_data = df[["PLAYER_NAME", "TEAM", col_name + suffix]].sort_values(by=col_name + suffix, ascending=False).head(5)
        if view_mode == "Tableau":
            col.markdown(f"### {title} {mode}") # Affiche le titre de la statistique
            col.dataframe(top_data, hide_index=True, use_container_width=True) # Affiche les données dans un tableau
        else:
            # Génère et affiche un diagramme en barres personnalisé
            fig = custom_bar_chart(top_data, col_name + suffix, f"{title}")
            col.plotly_chart(fig, use_container_width=True)

def show_defense(df, label, mode, view_mode):
    """
    Affiche les statistiques défensives des joueurs.
    """
    suffix = "_PG" if mode == "Par Match" else "" # Ajoute '_PG' si le mode est 'Par Match'
    st.markdown(f"##  Statistiques Défensives ({label} - {mode})") # Titre de la section

    stats = {
        "Rebonds Totaux": "REB",
        "Rebonds Défensifs": "DREB",
        "Contres": "BLK",
        "Interceptions": "STL"
    } # Dictionnaire des statistiques défensives à afficher

    col1, col2 = st.columns(2) # Crée 2 colonnes pour l'affichage des statistiques
    # Itère sur les statistiques et les colonnes pour les afficher
    for (title, col_name), col in zip(stats.items(), [col1, col2, col1, col2]):
        # Récupère les 5 meilleurs joueurs pour la statistique actuelle
        top_data = df[["PLAYER_NAME", "TEAM", col_name + suffix]].sort_values(by=col_name + suffix, ascending=False).head(5)
        if view_mode == "Tableau":
            col.markdown(f"### {title} {mode}") # Affiche le titre de la statistique
            col.dataframe(top_data, hide_index=True, use_container_width=True) # Affiche les données dans un tableau
        else:
            # Génère et affiche un diagramme en barres personnalisé
            fig = custom_bar_chart(top_data, col_name + suffix, f"{title}")
            col.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Affichage selon les Filtres
# -------------------------------
if metric_filter == "Leaders":
    # Affiche les leaders pour les statistiques offensives et défensives
    show_offense(df, season_filter, stat_mode, view_mode)
    st.divider() # Ajoute un séparateur visuel
    show_defense(df, season_filter, stat_mode, view_mode)

elif metric_filter == "Top 30":
    # Sélecteur de statistiques pour afficher le Top 30 des joueurs
    stat_choice = st.selectbox(
        "Sélectionnez une statistique",
        [
            "Points",
            "Passes Décisives",
            "Rebonds Totaux",
            "Rebonds Offensifs",
            "Rebonds Défensifs",
            "Minutes",
            "Tirs à 3 Points Réussis",
            "Lancers Francs Réussis",
            "Contres",
            "Interceptions",
            "Pertes de Balle",
        ]
    )
    suffix = "_PG" if stat_mode == "Par Match" else "" # Ajoute '_PG' si le mode est 'Par Match'
    # Mappage des noms de statistiques à leurs colonnes dans le DataFrame
    stat_map = {
        "Points": "PTS",
        "Passes Décisives": "AST",
        "Rebonds Totaux": "REB",
        "Rebonds Offensifs": "OREB",
        "Rebonds Défensifs": "DREB",
        "Minutes": "MIN",
        "Tirs à 3 Points Réussis": "FG3M",
        "Lancers Francs Réussis": "FTM",
        "Contres": "BLK",
        "Interceptions": "STL",
        "Pertes de Balle": "TOV",
    }

    # Construit le nom de la colonne à partir de la statistique choisie et du suffixe de mode
    chosen_col = stat_map[stat_choice] + suffix
    # Récupère le Top 30 des joueurs pour la statistique choisie
    top30 = (
        df[["PLAYER_NAME", "TEAM", chosen_col]]
        .sort_values(by=chosen_col, ascending=False)
        .head(30)
    )

    st.markdown(f"##  Top 30 {stat_choice} ({stat_mode}) - {season_filter}") # Titre du Top 30
    st.dataframe(top30, hide_index=True, use_container_width=True) # Affiche le Top 30 dans un tableau

elif metric_filter == "Données Complètes":
    st.markdown(f"## 📊 {season_filter} — Données Complètes (Style de Paramètre de Champ)") # Titre de la section

    # Étape 1 : Récupère toutes les colonnes disponibles, sauf "PLAYER_NAME"
    available_fields = [col for col in df.columns if col != "PLAYER_NAME"]

    # Étape 2 : Ajoute l'option "Tout sélectionner" en haut de la liste
    multiselect_options = ["Tout sélectionner"] + available_fields

    # Étape 3 : Widget de sélection multiple pour les colonnes à afficher
    selected_fields = st.multiselect(
        "Sélectionnez les colonnes à afficher",
        options=multiselect_options,
        default=available_fields[:3] # Sélectionne les 3 premières colonnes par défaut
    )

    # Étape 4 : Si "Tout sélectionner" est choisi, remplace par toutes les colonnes disponibles
    if "Tout sélectionner" in selected_fields:
        selected_fields = available_fields  # Toutes les colonnes réelles

    # Étape 5 : Affiche le tableau avec les colonnes sélectionnées
    if selected_fields:
        df_view = df[["PLAYER_NAME"] + selected_fields] # Construit le DataFrame à afficher
        st.dataframe(df_view, hide_index=True, use_container_width=True) # Affiche le DataFrame
    else:
        st.info("Veuillez sélectionner au moins une colonne à afficher. Le Nom du Joueur est sélectionné par défaut.") # Message si aucune colonne n'est choisie