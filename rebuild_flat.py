# rebuild_flat.py

import os
import pandas as pd

# ---------------------------
# Schémas fixes (toutes colonnes possibles)
# ---------------------------
RS_SCHEMA = [
    "RK", "PLAYER", "AGE", "TEAM", "POS", "G", "GS", "MP",
    "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "EFG%",
    "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS",
    "TRP-DBL", "AWARDS", "SEASON", "SEASON_TYPE",
    "MP_PG", "FG_PG", "FGA_PG", "3P_PG", "3PA_PG", "2P_PG", "2PA_PG",
    "FT_PG", "FTA_PG", "ORB_PG", "DRB_PG", "TRB_PG", "AST_PG", "STL_PG", "BLK_PG", "TOV_PG", "PF_PG", "PTS_PG",
    "SEASON_YEAR"
]

PO_SCHEMA = [
    "RK", "PLAYER", "POS", "AGE", "TEAM", "G", "GS", "MP",
    "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "EFG%",
    "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS",
    "SEASON", "SEASON_TYPE",
    "MP_PG", "FG_PG", "FGA_PG", "3P_PG", "3PA_PG", "2P_PG", "2PA_PG",
    "FT_PG", "FTA_PG", "ORB_PG", "DRB_PG", "TRB_PG", "AST_PG", "STL_PG", "BLK_PG", "TOV_PG", "PF_PG", "PTS_PG",
    "TEAM.1"
]

# ---------------------------
# Helpers
# ---------------------------
def concat_with_schema(folder: str, schema: list) -> pd.DataFrame:
    """Concatène tous les fichiers d’un dossier en respectant un schéma fixe."""
    if not os.path.exists(folder):
        print(f"⚠️ Dossier introuvable: {folder}")
        return pd.DataFrame(columns=schema)

    files = sorted([f for f in os.listdir(folder) if f.endswith(".csv")])
    if not files:
        print(f"⚠️ Aucun fichier trouvé dans {folder}")
        return pd.DataFrame(columns=schema)

    dfs = []
    for f in files:
        path = os.path.join(folder, f)
        try:
            df = pd.read_csv(path, encoding="utf-8-sig")
            df = df.reindex(columns=schema, fill_value=pd.NA)
            dfs.append(df)
            print(f"✅ {f} chargé ({len(df)} lignes)")
        except Exception as e:
            print(f"❌ Erreur lecture {f}: {e}")

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame(columns=schema)

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    os.makedirs("flat_table", exist_ok=True)

    # RS
    df_rs = concat_with_schema("processed_data_season_granularity/rs", RS_SCHEMA)
    df_rs.to_csv("flat_table/flat_rs_player.csv", index=False, encoding="utf-8-sig")
    print(f"🎉 Flat RS table créée avec {len(df_rs)} lignes")

    # PO
    df_po = concat_with_schema("processed_data_season_granularity/po", PO_SCHEMA)
    df_po.to_csv("flat_table/flat_po_player.csv", index=False, encoding="utf-8-sig")
    print(f"🎉 Flat PO table créée avec {len(df_po)} lignes")
