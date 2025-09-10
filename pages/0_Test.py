# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from nav import navbar # Assurez-vous que ce module est correctement importé si nécessaire


# -------------------------------
# Show navbar (si ce code est dans home.py, passez cette section)
# -------------------------------
# --- Top navbar (official) ---
# Si ce code est dans home.py, c'est ici que la correction st.columns(6) est nécessaire.
# Si c'est dans pages/4_Test.py, cette section peut être laissée telle quelle si elle ne cause pas d'erreur,
# ou retirée si ce n'est pas le point d'entrée de l'application.
# Pour l'exemple, je la garde telle quelle si elle n'est pas source de l'erreur dans 4_Test.py
c1, c2, c3, c4,c5,c6 = st.columns(6) # Correction ici pour home.py
with c1: st.page_link("home.py",                   label="🏠 Home")
with c2: st.page_link("pages/1_Team.py",           label="🏀 Team")
with c3: st.page_link("pages/2_Statistics.py",     label="📊 Statistics")
with c4: st.page_link("pages/3_Champ_Historic.py", label="🏆 Historic")
with c5: st.page_link("pages/4_Trade_Machine.py",  label="💸 Trade Machine")
with c6: st.page_link("pages/4_Test.py",  label="Test")


# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Trade Machine", layout="wide")



# -------------------------------
# Load Data
# -------------------------------
df_west = pd.read_excel("data/df_western_conf_standing.xlsx")
df_east = pd.read_excel("data/df_eastern_conf_standing.xlsx")
df_team_ratings = pd.read_excel("data/df_nba_team_reg_season_ratings.xlsx")
df_reg_players = pd.read_excel("data/df_reg_season_players_filtered.xlsx")
df_po_players = pd.read_excel("data/df_playoff_players_filtered.xlsx")

# Chemin du fichier de salaires
salaries_excel_path = "data/df_nba_players_salaries.xlsx"
salaries_csv_temp_path = "data/df_nba_players_salaries_temp.csv" # Fichier CSV temporaire

st.write("Chargement de df_salaries depuis Excel...")
df_salaries = pd.read_excel(salaries_excel_path)
#st.dataframe(df_salaries) # Affiche le DataFrame tel qu'il est lu initialement

# --- Début de la correction d'encodage via CSV ---
st.subheader("Processus de correction de l'encodage")

try:
    # 1. Sauvegarder le DataFrame actuel en CSV avec encodage UTF-8
    st.write(f"Sauvegarde temporaire de '{salaries_excel_path}' en CSV UTF-8 : '{salaries_csv_temp_path}'...")
    df_salaries.to_csv(salaries_csv_temp_path, index=False, encoding='utf-8')
    st.success("Sauvegarde CSV temporaire réussie.")

    # 2. Recharger le DataFrame depuis le CSV avec encodage UTF-8
    st.write(f"Rechargement du DataFrame depuis le fichier CSV UTF-8...")
    df_salaries_corrected = pd.read_csv(salaries_csv_temp_path, encoding='utf-8')
    st.success("Rechargement CSV réussi. Vérification des données...")

    # 3. Afficher le DataFrame corrigé pour vérification
    st.write("DataFrame après correction (visualisation) :")
    st.dataframe(df_salaries_corrected)

    """
    # 4. Enregistrer le DataFrame corrigé dans le fichier Excel d'origine, écrasant l'ancien
    st.write(f"Sauvegarde du DataFrame corrigé dans le fichier Excel d'origine : '{salaries_excel_path}'...")
    df_salaries_corrected.to_excel(salaries_excel_path, index=False)
    st.success(f"L'encodage de '{salaries_excel_path}' a été corrigé et le fichier a été mis à jour.")

    # Optionnel: Supprimer le fichier CSV temporaire après l'opération
    import os
    if os.path.exists(salaries_csv_temp_path):
        os.remove(salaries_csv_temp_path)
        st.info("Fichier CSV temporaire supprimé.")

    # Mettre à jour df_salaries avec la version corrigée pour la suite du script
    df_salaries = df_salaries_corrected
    """
except Exception as e:
    st.error(f"Une erreur est survenue lors de la correction de l'encodage : {e}")

# --- Fin de la correction d'encodage ---

# st.dataframe(df_) # <-- C'est ici que l'erreur 'df_' n'est pas définie apparaissait.
                   # Si vous voulez afficher le df corrigé, utilisez df_salaries.
                   # Sinon, retirez cette ligne.

# Votre code Streamlit continue ici avec df_salaries qui est maintenant corrigé
# ... (le reste de votre application)"""