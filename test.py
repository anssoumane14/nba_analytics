import os
import pandas as pd
import streamlit as st

# -------------------------------
# Config
# -------------------------------
st.set_page_config(layout="wide")

# -------------------------------
# Charger les flat tables
# -------------------------------
FLAT_DIR = "flat_table"

# On prend uniquement les fichiers CSV
flat_files = [f for f in os.listdir(FLAT_DIR) if f.endswith(".csv")]

st.markdown("<h1 style='text-align: center;'>📑 Colonnes des Flat Tables</h1>", unsafe_allow_html=True)

for file in sorted(flat_files):
    st.subheader(f"📂 {file}")
    path = os.path.join(FLAT_DIR, file)

    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        # Affiche les colonnes
        st.write(list(df.columns))
        # Un petit aperçu des données
        st.dataframe(df.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Erreur lors du chargement de {file} : {e}")
