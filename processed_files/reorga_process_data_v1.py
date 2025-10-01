import os
import pandas as pd
import re
from functions import clean_table, clean_awards, clean_honors, clean_player_stats

RAW_BASE = "raw_data"
PROC_BASE = "processed_data"
os.makedirs(PROC_BASE, exist_ok=True)

def process_and_save(raw_folder, out_folder, cleaner=None):
    """Applique un nettoyage sur un dossier brut et écrase les fichiers dans processed_data."""
    os.makedirs(out_folder, exist_ok=True)
    for file in os.listdir(raw_folder):
        if not file.endswith(".csv"):
            continue

        path_in = os.path.join(raw_folder, file)
        df = pd.read_csv(path_in, encoding="utf-8-sig")

        # appliquer le bon nettoyeur
        if cleaner:
            df = cleaner(df)
        else:
            table_type = re.sub(r"_\d{4}.csv$", "", file)
            df = clean_table(df, table_type)

        # sauvegarde avec le même nom
        path_out = os.path.join(out_folder, file)
        df.to_csv(path_out, index=False, encoding="utf-8-sig")
        print(f"✅ {file} nettoyé → {path_out} ({len(df)} lignes)")


if __name__ == "__main__":

    # --- TEAM STATS ---
    for folder in ["east_standing", "west_standing", "team_tot_stats",
                   "team_pg_stats", "team_per_poss_stats", "team_adv_stats"]:
        process_and_save(f"{RAW_BASE}/{folder}", f"{PROC_BASE}/{folder}")

    # --- PLAYER STATS ---
    for folder in ["rs", "po", "advanced", "per_poss", "play-by-play"]:
        process_and_save(f"{RAW_BASE}/{folder}", f"{PROC_BASE}/{folder}", clean_player_stats)

    # --- HONORS ---
    for folder in ["all_nba_teams", "all_def_teams", "all_rookie_teams", "all_star_teams"]:
        process_and_save(f"{RAW_BASE}/{folder}", f"{PROC_BASE}/{folder}", clean_honors)

    # --- AWARDS ---
    process_and_save(f"{RAW_BASE}/awards", f"{PROC_BASE}/awards", clean_awards)
