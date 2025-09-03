# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from nav import navbar # Importation potentielle de la barre de navigation

# -------------------------------
# Configuration de la Page
# -------------------------------
st.set_page_config(page_title="Tableau de Bord NBA", layout="wide") # Configure le titre de la page et la disposition large

# -------------------------------
# Affichage de la Barre de Navigation
# -------------------------------
# Note : La barre de navigation est actuellement implémentée directement via st.page_link
# Pour une implémentation modulable, l'utilisation de la fonction navbar() importée serait envisagée.
c1, c2, c3, c4,c5 = st.columns(5) # Crée 5 colonnes pour les liens de navigation
with c1: st.page_link("home.py",                   label="🏠 Accueil") # Lien vers la page d'accueil
with c2: st.page_link("pages/1_Team.py",           label="🏀 Équipe") # Lien vers la page d'équipe
with c3: st.page_link("pages/2_Statistics.py",     label="📊 Statistiques") # Lien vers la page de statistiques
with c4: st.page_link("pages/3_Champ_Historic.py", label="🏆 Historique") # Lien vers la page historique des champions
with c5: st.page_link("pages/4_Trade_Machine.py",  label="💸 Machine à Trade") # Lien vers la machine à trade


# -------------------------------
# Chargement des Données
# -------------------------------
df_west = pd.read_excel("data/df_western_conf_standing.xlsx") # Charge les classements de la Conférence Ouest
df_east = pd.read_excel("data/df_eastern_conf_standing.xlsx") # Charge les classements de la Conférence Est
df_team_ratings = pd.read_excel("data/df_nba_team_reg_season_ratings.xlsx") # Charge les évaluations des équipes de saison régulière
df_players = pd.read_excel("data/df_reg_season_players_filtered.xlsx") # Charge les données filtrées des joueurs de saison régulière
df_salaries = pd.read_excel("data/df_nba_players_salaries.xlsx") # Charge les salaires des joueurs

# Applique un filtre additionnel aux joueurs : uniquement ceux ayant joué plus de 10 matchs et plus de 10 minutes par match
df_players = df_players[(df_players["GP"] > 10) & (df_players["MIN_PG"] > 10)]


# -------------------------------
# Titre de la Page
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>🏀 Aperçu NBA 2024-25</h1>",
    unsafe_allow_html=True # Permet le rendu HTML
)
st.markdown(
    "<h4 style='text-align: center; color: gray;'>Un Regard Global sur la Ligue</h4>",
    unsafe_allow_html=True # Permet le rendu HTML
)


# -------------------------------
# Onglets de Navigation
# -------------------------------
# Crée des onglets pour organiser le contenu de la page
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Classements des Conférences",
    "⭐ Meilleurs Joueurs",
    "📊 Évaluations des Équipes",
    "💰 Salaires"
])

# -------------------------------
# Contenu de l'Onglet 1 : Classements des Conférences
# -------------------------------
with tab1:
    st.markdown("## 🏆 Classements des Conférences") # Titre de l'onglet

    col1, col2 = st.columns(2) # Crée deux colonnes pour afficher les conférences côte à côte
    with col1:
        st.markdown("### Conférence Ouest") # Sous-titre pour la Conférence Ouest
        st.dataframe(df_west, hide_index=True, use_container_width=True) # Affiche le DataFrame de la Conférence Ouest
    with col2:
        st.markdown("### Conférence Est") # Sous-titre pour la Conférence Est
        st.dataframe(df_east, hide_index=True, use_container_width=True) # Affiche le DataFrame de la Conférence Est

# -------------------------------
# Contenu de l'Onglet 2 : Meilleurs Joueurs
# -------------------------------
with tab2:
    st.markdown("## ⭐ Top 3 des Joueurs par Métriques Clés") # Titre de l'onglet

    # Filtre de sélection d'équipe unique avec l'option "Toutes les équipes"
    all_teams = sorted(df_players["TEAM"].dropna().unique()) # Récupère la liste unique des équipes
    team_choice = st.selectbox(
        "Équipe",
        options=["Toutes les équipes"] + all_teams, # Ajoute "Toutes les équipes" comme première option
        index=0, # Sélectionne la première option par défaut
        key="top_players_team_filter_single" # Clé unique pour le widget
    )

    # Applique le filtre localement
    df_tp = df_players.copy() # Crée une copie du DataFrame des joueurs
    if team_choice != "Toutes les équipes": # Si une équipe spécifique est choisie
        df_tp = df_tp[df_tp["TEAM"] == team_choice] # Filtre le DataFrame par l'équipe sélectionnée

    metrics = {
        "Points Par Match": "PTS_PG",
        "Rebonds Par Match": "REB_PG",
        "Passes Décisives Par Match": "AST_PG"
    } # Dictionnaire des métriques à afficher

    # Itère sur chaque métrique pour afficher les 3 meilleurs joueurs
    for label, col_name in metrics.items():
        if col_name not in df_tp.columns: # Vérifie si la colonne existe dans le DataFrame
            st.warning(f"La colonne '{col_name}' n'a pas été trouvée dans les données des joueurs.")
            continue # Passe à la métrique suivante si la colonne est manquante

        top3 = (
            df_tp[["PLAYER_NAME", "TEAM", col_name]] # Sélectionne les colonnes Joueur, Équipe et la métrique
            .sort_values(by=col_name, ascending=False) # Trie par la métrique en ordre décroissant
            .head(3) # Prend les 3 premiers joueurs
        )
        st.markdown(f"### {label}") # Affiche le titre de la métrique
        st.dataframe(top3, hide_index=True, use_container_width=True) # Affiche le DataFrame des 3 meilleurs

# -------------------------------
# Contenu de l'Onglet 3 : Évaluations des Équipes
# -------------------------------
with tab3:
    st.markdown("## 📊 Évaluations de Performance des Équipes (Top 10)") # Titre de l'onglet

    col1, col2, col3 = st.columns(3) # Crée trois colonnes pour les différentes évaluations

    # Offensive Rating (plus élevé est mieux)
    with col1:
        st.markdown("### Évaluation Offensive") # Sous-titre
        if "ORTG" in df_team_ratings.columns: # Vérifie si la colonne existe
            off = df_team_ratings[["TEAM", "ORTG"]].sort_values(by="ORTG", ascending=False).head(10) # Trie et prend les 10 meilleures
            st.dataframe(off, hide_index=True, use_container_width=True) # Affiche le DataFrame
        else:
            st.warning("La colonne 'ORTG' n'a pas été trouvée dans les évaluations des équipes.")

    # Defensive Rating (plus faible est mieux → ordre croissant)
    with col2:
        st.markdown("### Évaluation Défensive") # Sous-titre
        if "DRTG" in df_team_ratings.columns: # Vérifie si la colonne existe
            deff = df_team_ratings[["TEAM", "DRTG"]].sort_values(by="DRTG", ascending=True).head(10) # Trie et prend les 10 meilleures
            st.dataframe(deff, hide_index=True, use_container_width=True) # Affiche le DataFrame
        else:
            st.warning("La colonne 'DRTG' n'a pas été trouvée dans les évaluations des équipes.")

    # Net Rating (plus élevé est mieux)
    with col3:
        st.markdown("### Évaluation Nette") # Sous-titre
        if "NRTG" in df_team_ratings.columns: # Vérifie si la colonne existe
            net = df_team_ratings[["TEAM", "NRTG"]].sort_values(by="NRTG", ascending=False).head(10) # Trie et prend les 10 meilleures
            st.dataframe(net, hide_index=True, use_container_width=True) # Affiche le DataFrame
        else:
            st.warning("La colonne 'NRTG' n'a pas été trouvée dans les évaluations des équipes.")

# -------------------------------
# Contenu de l'Onglet 4 : Salaires (filtres simples)
# -------------------------------

with tab4:
    st.markdown("## 💰 Salaires") # Titre de l'onglet

    # Filtre d'équipe
    team_options = ["Toutes les équipes"] + sorted(df_salaries["TEAM"].dropna().unique()) # Liste des équipes pour le filtre
    team_sel = st.selectbox("Équipe", team_options, index=0) # Sélecteur d'équipe

    # Filtre le DataFrame par l'équipe sélectionnée
    df_filtered = df_salaries.copy() # Crée une copie du DataFrame des salaires
    if team_sel != "Toutes les équipes": # Si une équipe spécifique est choisie
        df_filtered = df_filtered[df_filtered["TEAM"] == team_sel] # Filtre le DataFrame

    # Filtre joueur (dépend du DataFrame filtré par équipe)
    player_options = ["Tous les joueurs"] + sorted(df_filtered["PLAYER"].dropna().unique()) # Liste des joueurs pour le filtre
    player_sel = st.selectbox("Joueur", player_options, index=0) # Sélecteur de joueur

    # Applique le filtre joueur
    if player_sel != "Tous les joueurs": # Si un joueur spécifique est choisi
        df_filtered = df_filtered[df_filtered["PLAYER"] == player_sel] # Filtre le DataFrame

    # Affiche le tableau filtré
    st.dataframe(df_filtered, hide_index=True, use_container_width=True) # Affiche le DataFrame des salaires filtré