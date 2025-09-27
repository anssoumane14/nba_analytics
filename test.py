import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

# -------------------------------
# Load Data
# -------------------------------
df_rs_all = pd.read_csv("processed_data/flat_rs_all.csv", encoding="utf-8-sig")
df_po_all = pd.read_csv("processed_data/flat_po_all.csv", encoding="utf-8-sig")
df_award_all = pd.read_csv("processed_data/flat_award_all.csv", encoding="utf-8-sig")

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filtres")

# Season filter
seasons = sorted(df_rs_all["Season"].dropna().unique(), reverse=True)
selected_season = st.sidebar.selectbox("Choisir une saison", seasons)

# Season type (Regular vs Playoffs)
season_type = st.sidebar.radio("Partie de la saison", ["Regular Season", "Playoffs"])

# -------------------------------
# Display Data
# -------------------------------
st.title("📊 NBA Player Statistics")

if season_type == "Regular Season":
    df_display = df_rs_all[df_rs_all["Season"] == selected_season]
else:
    df_display = df_po_all[df_po_all["Season"] == selected_season]

st.subheader(f"Statistiques — {season_type} — {selected_season}")
st.dataframe(df_display, use_container_width=True, hide_index=True)

# -------------------------------
# Awards Section
# -------------------------------
st.title("🏆 NBA Awards")

df_awards_display = df_award_all[df_award_all["Season"] == selected_season]
st.dataframe(df_awards_display, use_container_width=True, hide_index=True)
