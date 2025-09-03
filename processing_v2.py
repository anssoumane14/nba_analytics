# -*- coding: utf-8 -*-
"""Deuxième passe de traitement : ajoute/normalise les positions des joueurs, prévisualise, puis écrase les fichiers Excel."""

import time
import pandas as pd
import streamlit as st
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster

# -------------------------------
# Configuration
# -------------------------------
SEASON   = "2024-25" # Saison de référence pour les données
REG_PATH = "data/df_reg_season_players.xlsx" # Chemin vers le fichier des joueurs de saison régulière
PO_PATH  = "data/df_playoff_players.xlsx" # Chemin vers le fichier des joueurs de playoffs

st.set_page_config(layout="wide") # Configuration de la mise en page Streamlit
st.title("Traitement v2 — Ajout des Positions des Joueurs") # Titre affiché par Streamlit

# -------------------------------
# Chargement des Données Existantes
# -------------------------------
# Charge les DataFrames des joueurs traités lors de la passe précédente
df_reg = pd.read_excel(REG_PATH)
df_po  = pd.read_excel(PO_PATH)

# Affiche un aperçu des DataFrames chargés (commenté pour la production)
#st.dataframe(df_reg)
#st.dataframe(df_po)

# -------------------------------
# Récupération des Positions des Effectifs (avec réessai et limitation)
# -------------------------------
pos_frames = [] # Liste pour stocker les DataFrames de positions de chaque équipe
failed = [] # Liste pour enregistrer les noms des équipes dont la récupération a échoué

team_list = teams.get_teams() # Récupère la liste de toutes les équipes NBA
progress = st.progress(0) # Barre de progression Streamlit
total = len(team_list) # Nombre total d'équipes à traiter

# Itère sur chaque équipe pour récupérer la composition de l'effectif
for i, t in enumerate(team_list, start=1):
    team_id = t["id"] # ID numérique de l'équipe
    name = t.get("full_name", t.get("abbreviation", str(team_id))) # Nom complet ou abréviation de l'équipe

    got = False # Indicateur de succès de la récupération
    # Tente de récupérer les données jusqu'à 4 fois en cas d'échec
    for attempt in range(4):
        try:
            # Récupère l'effectif de l'équipe pour la saison donnée
            roster = commonteamroster.CommonTeamRoster(
                team_id=team_id, season=SEASON, timeout=90
            ).get_data_frames()[0]
            # Ajoute les colonnes PLAYER_ID, PLAYER et POSITION à la liste
            pos_frames.append(roster[["PLAYER_ID", "PLAYER", "POSITION"]])
            got = True # Marque comme réussi
            break # Sort de la boucle de réessai
        except Exception:
            # En cas d'erreur, attend avant de réessayer (backoff exponentiel simple)
            time.sleep(0.8 * (attempt + 1))
    if not got:
        # Si la récupération échoue après tous les réessais, ajoute l'équipe à la liste des échecs
        failed.append(name)

    time.sleep(0.5) # Petite pause pour limiter les requêtes à l'API (throttling)
    progress.progress(i / total) # Met à jour la barre de progression

# Affiche un avertissement si certaines données d'effectif n'ont pas pu être récupérées
if failed:
    st.warning(f"Impossible de récupérer l'effectif pour : {', '.join(failed)}")

# Arrête l'exécution si aucune donnée d'effectif n'a pu être récupérée
if not pos_frames:
    st.error("Aucune donnée d'effectif récupérée après plusieurs tentatives. Veuillez réessayer dans une minute.")
    st.stop()

# Concatène tous les DataFrames de positions en un seul
df_positions = pd.concat(pos_frames, ignore_index=True)

# Conserve uniquement les colonnes nécessaires et assure une seule ligne par joueur
df_positions = (
    df_positions[["PLAYER_ID", "POSITION"]]
    .dropna(subset=["PLAYER_ID"]) # Supprime les lignes avec un PLAYER_ID manquant
    .drop_duplicates(subset=["PLAYER_ID"], keep="last") # Supprime les doublons de PLAYER_ID, en gardant la dernière entrée
)

# -------------------------------
# Fusion des Positions (jointure à gauche sur PLAYER_ID)
# -------------------------------
# Fusionne les positions récupérées avec les DataFrames de joueurs existants
df_reg = df_reg.merge(df_positions, how="left", on="PLAYER_ID", validate="m:1")
df_po  = df_po.merge(df_positions, how="left", on="PLAYER_ID", validate="m:1")

# Affiche les DataFrames fusionnés (commenté pour la production)
#st.dataframe(df_reg)
#st.dataframe(df_po)


# Si la fusion a créé des colonnes 'POSITION_x' / 'POSITION_y', renomme la colonne provenant de l'effectif en 'POS'
if "POSITION_x" in df_reg.columns:
    df_reg.rename(columns={"POSITION_x": "POS"}, inplace=True)
if "POSITION_x" in df_po.columns:
    df_po.rename(columns={"POSITION_x": "POS"}, inplace=True)

# Supprime toute colonne 'POSITION_y' restante pour éviter la confusion
for df_ in (df_reg, df_po):
    if "POSITION_y" in df_.columns:
        df_.drop(columns=["POSITION_y"], inplace=True)


# -------------------------------
# Cartographie vers des Étiquettes Plus Compréhensibles
# -------------------------------
# Dictionnaire pour mapper les abréviations de position de l'API à des noms complets et familiers
position_map = {
    "G":   "Guard",
    "F":   "Forward",
    "C":   "Center",
    "G-F": "Guard",          # Règle choisie : "G-F" est catégorisé comme "Guard"
    "F-G": "Small Forward",  # Règle choisie : "F-G" est catégorisé comme "Small Forward"
    "F-C": "Power Forward",
    "C-F": "Center",
}

# Applique la cartographie à la colonne 'POS' pour créer la colonne 'POSITION' (plus lisible)
# S'assure que 'POS' est bien une série (colonne unique) avant d'appliquer la cartographie
df_reg["POSITION"] = df_reg["POS"].map(position_map).fillna("Unknown") # Remplace les valeurs non mappées par "Unknown"
df_po["POSITION"]  = df_po["POS"].map(position_map).fillna("Unknown")  # Remplace les valeurs non mappées par "Unknown"

"""# -------------------------------
# Écrasement des Fichiers Excel
# -------------------------------
# Sauvegarde les DataFrames mis à jour avec les positions dans les fichiers Excel originaux
df_reg.to_excel(REG_PATH, index=False)
df_po.to_excel(PO_PATH, index=False)

st.success("Fichiers Excel mis à jour avec POS (brut) et POSITION (lisible)")
st.write(f"- {REG_PATH}")
st.write(f"- {PO_PATH}")

# Affiche un aperçu des colonnes de position pour vérification (commenté pour la production)
st.dataframe(df_po[["PLAYER_NAME","TEAM","POS","POSITION"]])
st.dataframe(df_reg[["PLAYER_NAME","TEAM","POS","POSITION"]])"""