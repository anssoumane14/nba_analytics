# processed_data_season_granularity.py

import os
import pandas as pd
import streamlit as st

# ---------------------------
# Helpers
# ---------------------------
def process_season_granularity(input_folder: str, output_folder: str):
    """
    Réduit à une seule ligne par joueur + saison :
    - Si 1 seule équipe → conserve la ligne telle quelle
    - Si plusieurs équipes → prend la ligne nTM (2TM, 3TM, 5TM...) et concatène les noms réels
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

        final_rows = []

        # groupement par joueur + saison + type de saison
        group_keys = ["PLAYER", "SEASON", "SEASON_TYPE"]
        for keys, group in df.groupby(group_keys):
            if len(group) == 1:
                final_rows.append(group.iloc[0])  # mono-équipe

            else:
                # chercher ligne nTM
                ntm_rows = group[group["TEAM"].str.match(r"\d+TM", na=False)]
                if not ntm_rows.empty:
                    ntm_row = ntm_rows.iloc[0].copy()
                else:
                    print(f"⚠️ Pas de nTM trouvé pour {keys}, on prend la première ligne")
                    ntm_row = group.iloc[0].copy()

                # concaténer les équipes réelles (hors nTM)
                real_teams = group[~group["TEAM"].str.match(r"\d+TM", na=False)]["TEAM"].tolist()
                teams_concat = " / ".join(real_teams)

                # remplacer TEAM par concaténation
                ntm_row["TEAM"] = teams_concat

                final_rows.append(ntm_row)

        df_final = pd.DataFrame(final_rows)

        # sauvegarde
        path_out = os.path.join(output_folder, file)
        df_final.to_csv(path_out, index=False, encoding="utf-8-sig")

        all_dfs.append(df_final)

        # log console
        print("✅ Input sample:")
        print(df.head(3))
        print("✅ Output sample:")
        print(df_final.head(3))
        print("-" * 50)

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame()


def display_kpis(df):
    """Affiche les KPIs principaux après filtre"""
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
# Main
# ---------------------------
if __name__ == "__main__":
    # Regular Season
    df_rs_final = process_season_granularity(
        input_folder="processed_data_team_map_1/rs",
        output_folder="processed_data_season_granularity/rs"
    )

    # Playoffs
    df_po_final = process_season_granularity(
        input_folder="processed_data_team_map_1/po",
        output_folder="processed_data_season_granularity/po"
    )

    print("\n🎉 Step processed_data_season_granularity terminé !")

    # ---------------------------
    # Streamlit Dashboard
    # ---------------------------
    st.title("📊 Processed Data Season Granularity Viewer")

    tab1, tab2 = st.tabs(["Regular Season", "Playoffs"])

    with tab1:
        if not df_rs_final.empty:
            st.subheader("Regular Season Data")

            players = sorted(df_rs_final["PLAYER"].dropna().unique())
            seasons = sorted(df_rs_final["SEASON"].dropna().unique())

            player = st.selectbox("Select Player", ["All"] + players)
            season = st.selectbox("Select Season", ["All"] + seasons)

            df_display = df_rs_final.copy()
            if player != "All":
                df_display = df_display[df_display["PLAYER"] == player]
            if season != "All":
                df_display = df_display[df_display["SEASON"] == season]

            # KPIs
            display_kpis(df_display)

            # Table
            st.dataframe(df_display)

    with tab2:
        if not df_po_final.empty:
            st.subheader("Playoffs Data")

            players = sorted(df_po_final["PLAYER"].dropna().unique())
            seasons = sorted(df_po_final["SEASON"].dropna().unique())

            player = st.selectbox("Select Player", ["All"] + players, key="po_player")
            season = st.selectbox("Select Season", ["All"] + seasons, key="po_season")

            df_display = df_po_final.copy()
            if player != "All":
                df_display = df_display[df_display["PLAYER"] == player]
            if season != "All":
                df_display = df_display[df_display["SEASON"] == season]

            # KPIs
            display_kpis(df_display)

            # Table
            st.dataframe(df_display)
