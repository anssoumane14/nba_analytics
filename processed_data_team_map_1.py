# processed_data_team_map_1.py

import os
import pandas as pd
import streamlit as st
from functions import map_team_names
def display_kpis(df):
    """Affiche les KPIs principaux après filtre (totaux + moyennes pondérées)."""
    if df.empty:
        return

    total_pts = df["PTS"].sum() if "PTS" in df.columns else None
    total_ast = df["AST"].sum() if "AST" in df.columns else None
    total_trb = df["TRB"].sum() if "TRB" in df.columns else None
    total_games = df["G"].sum() if "G" in df.columns else None

    mean_pts = (total_pts / total_games) if total_pts and total_games else None
    mean_ast = (total_ast / total_games) if total_ast and total_games else None
    mean_trb = (total_trb / total_games) if total_trb and total_games else None

    st.markdown("### 📌 KPIs Résumés")
    cols = st.columns(4)
    cols[0].metric("Total PTS", f"{total_pts:.0f}" if total_pts else "N/A")
    cols[1].metric("Total AST", f"{total_ast:.0f}" if total_ast else "N/A")
    cols[2].metric("Total TRB", f"{total_trb:.0f}" if total_trb else "N/A")
    cols[3].metric("Total Games", f"{total_games:.0f}" if total_games else "N/A")

    cols = st.columns(3)
    cols[0].metric("PTS_PG (avg)", f"{mean_pts:.1f}" if mean_pts else "N/A")
    cols[1].metric("AST_PG (avg)", f"{mean_ast:.1f}" if mean_ast else "N/A")
    cols[2].metric("TRB_PG (avg)", f"{mean_trb:.1f}" if mean_trb else "N/A")

# ---------------------------
# Helpers
# ---------------------------
def process_team_map(input_folder: str, output_folder: str, abbr_col: str):
    """
    Applique le mapping des équipes (abbr → noms complets).
    RS utilise TEAM, PO utilise TM.
    """
    os.makedirs(output_folder, exist_ok=True)
    all_dfs = []

    for file in os.listdir(input_folder):
        if not file.endswith(".csv"):
            continue

        print(f"⏳ Processing {file} ...")

        # lecture
        path_in = os.path.join(input_folder, file)
        df = pd.read_csv(path_in, encoding="utf-8-sig")

        # mapping
        df_map = map_team_names(df, abbr_col=abbr_col)

        # si PO : renommer TM en TEAM
        if abbr_col == "TM" and "TM" in df_map.columns:
            df_map.rename(columns={"TM": "TEAM"}, inplace=True)

        # sauvegarde
        path_out = os.path.join(output_folder, file)
        df_map.to_csv(path_out, index=False, encoding="utf-8-sig")

        # concat pour affichage global
        all_dfs.append(df_map)

        # log console
        print("✅ Input sample:")
        print(df.head(3))
        print("✅ Output sample:")
        print(df_map.head(3))
        print("-" * 50)

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame()


# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    # Regular Season
    df_rs_map = process_team_map(
        input_folder="processed_data_pg/rs",
        output_folder="processed_data_team_map_1/rs",
        abbr_col="TEAM"
    )

    # Playoffs
    df_po_map = process_team_map(
        input_folder="processed_data_pg/po",
        output_folder="processed_data_team_map_1/po",
        abbr_col="TM"
    )

    print("\n🎉 Step processed_data_team_map_1 terminé !")

    # ---------------------------
    # Streamlit Dashboard
    # ---------------------------
    st.title("📊 Processed Data Team Map Viewer")

    tab1, tab2 = st.tabs(["Regular Season", "Playoffs"])

    with tab1:
        if not df_rs_map.empty:
            st.subheader("Regular Season Data")

            players = sorted(df_rs_map["PLAYER"].dropna().unique())
            seasons = sorted(df_rs_map["SEASON"].dropna().unique())
            teams = sorted(df_rs_map["TEAM"].dropna().unique())

            player = st.selectbox("Select Player", ["All"] + players)
            season = st.selectbox("Select Season", ["All"] + seasons)
            team = st.selectbox("Select Team", ["All"] + teams)

            df_display = df_rs_map.copy()
            if player != "All":
                df_display = df_display[df_display["PLAYER"] == player]
            if season != "All":
                df_display = df_display[df_display["SEASON"] == season]
            if team != "All":
                df_display = df_display[df_display["TEAM"] == team]

            st.dataframe(df_display)
            display_kpis(df_display)


    with tab2:
        if not df_po_map.empty:
            st.subheader("Playoffs Data")

            players = sorted(df_po_map["PLAYER"].dropna().unique())
            seasons = sorted(df_po_map["SEASON"].dropna().unique())
            teams = sorted(df_po_map["TEAM"].dropna().unique())

            player = st.selectbox("Select Player", ["All"] + players, key="po_player")
            season = st.selectbox("Select Season", ["All"] + seasons, key="po_season")
            team = st.selectbox("Select Team", ["All"] + teams, key="po_team")

            df_display = df_po_map.copy()
            if player != "All":
                df_display = df_display[df_display["PLAYER"] == player]
            if season != "All":
                df_display = df_display[df_display["SEASON"] == season]
            if team != "All":
                df_display = df_display[df_display["TEAM"] == team]

            st.dataframe(df_display)
            display_kpis(df_display)

