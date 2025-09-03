# -*- coding: utf-8 -*-
"""Troisième passe de traitement : Nettoyage et Filtrage des Joueurs"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Traitement v3 — Filtres", layout="wide") # Configuration de la page Streamlit
st.title("Traitement v3 — Nettoyage des Joueurs") # Titre affiché par Streamlit

# -------------------------------
# Chargement des Données
# -------------------------------
REG_PATH = "data/df_reg_season_players.xlsx" # Chemin vers le fichier des joueurs de saison régulière
PO_PATH  = "data/df_playoff_players.xlsx" # Chemin vers le fichier des joueurs de playoffs

# Charge les DataFrames des joueurs qui ont été enrichis par la v2 du traitement
df_reg = pd.read_excel(REG_PATH)
df_po  = pd.read_excel(PO_PATH)

# -------------------------------
# Opérations de Filtrage
# -------------------------------
def clean_players(df):
    """
    Applique des filtres de qualité aux données des joueurs.
    """
    # Supprime les joueurs dont la position est 'Unknown' (inconnue),
    # car ces entrées sont souvent le signe de données incomplètes ou incorrectes.
    if "POSITION" in df.columns:
        df = df[df["POSITION"] != "Unknown"]

    # Supprime les joueurs ayant joué 5 minutes ou moins par match.
    # Ce filtre permet de se concentrer sur les joueurs ayant un temps de jeu significatif,
    # rendant les statistiques plus représentatives de leur performance réelle.
    if "MIN_PG" in df.columns:
        df = df[df["MIN_PG"] > 5]

    return df

# Applique la fonction de nettoyage aux DataFrames de saison régulière et de playoffs
df_reg_clean = clean_players(df_reg)
df_po_clean  = clean_players(df_po)

# -------------------------------
# Sauvegarde des Données Nettoyées
# -------------------------------
# Sauvegarde les DataFrames filtrés dans de nouveaux fichiers Excel.
# L'ajout du suffixe '_filtered' permet de distinguer clairement ces fichiers des précédents,
# marquant cette étape comme la finalisation du traitement des données des joueurs.
df_reg_clean.to_excel("data/df_reg_season_players_filtered.xlsx", index=False)
df_po_clean.to_excel("data/df_playoff_players_filtered.xlsx", index=False)

st.success("Fichiers filtrés sauvegardés !") # Message de confirmation affiché par Streamlit