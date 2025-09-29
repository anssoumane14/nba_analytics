import os
import shutil
import re

RAW_BASE = "raw_data_bball_ref"
CLEAN_BASE = "raw_data"

def ensure_dir(path):
    """Créer le dossier si inexistant"""
    os.makedirs(path, exist_ok=True)

def copy_and_rename(src, dst_folder, new_name):
    """Copie et renomme un fichier"""
    ensure_dir(dst_folder)
    dst = os.path.join(dst_folder, new_name)
    shutil.copy(src, dst)
    print(f"✅ {src} → {dst}")

def reorganize_raw():
    ensure_dir(CLEAN_BASE)

    # --- 1. Advanced ---
    src_folder = os.path.join(RAW_BASE, "raw_advanced")
    dst_folder = os.path.join(CLEAN_BASE, "advanced")
    ensure_dir(dst_folder)

    for file in os.listdir(src_folder):
        if file.startswith("df_advanced") and file.endswith(".csv"):
            # df_advanced_rs_2025.csv → advanced_rs_2025.csv
            parts = file.replace(".csv", "").split("_")
            _, _, season_type, year = parts
            new_name = f"advanced_{season_type}_{year}.csv"
            copy_and_rename(os.path.join(src_folder, file), dst_folder, new_name)

    # --- 2. All Teams (nba, def, rookie, star) ---
    for t in ["nba", "def", "rookie", "star"]:
        src_folder = os.path.join(RAW_BASE, f"raw_all_{t}_teams")
        dst_folder = os.path.join(CLEAN_BASE, f"all_{t}_teams")
        ensure_dir(dst_folder)

        for file in os.listdir(src_folder):
            if file.endswith(".csv"):
                # raw_raw_all_{t}_teams_1975-76.csv → all_{t}_teams_1976.csv
                match = re.search(r"(\d{4})-(\d{2})", file)
                if match:
                    year = match.group(1)  # garder que l'année finale
                    new_name = f"all_{t}_teams_{year}.csv"
                    copy_and_rename(os.path.join(src_folder, file), dst_folder, new_name)

    # --- 3. Awards ---
    src_folder = os.path.join(RAW_BASE, "raw_award")
    dst_folder = os.path.join(CLEAN_BASE, "awards")
    ensure_dir(dst_folder)

    for file in os.listdir(src_folder):
        if file.startswith("df_awards") and file.endswith(".csv"):
            # df_awards_2025.csv → awards_2025.csv
            year = file.split("_")[-1].replace(".csv", "")
            new_name = f"awards_{year}.csv"
            copy_and_rename(os.path.join(src_folder, file), dst_folder, new_name)

    # --- 4. Per Poss ---
    src_folder = os.path.join(RAW_BASE, "raw_per_poss")
    dst_folder = os.path.join(CLEAN_BASE, "per_poss")
    ensure_dir(dst_folder)

    for file in os.listdir(src_folder):
        if file.startswith("df_per_poss") and file.endswith(".csv"):
            year = file.split("_")[-1].replace(".csv", "")
            new_name = f"per_poss_{year}.csv"
            copy_and_rename(os.path.join(src_folder, file), dst_folder, new_name)

    # --- 5. Play-by-Play, RS, PO ---
    for sub in ["raw_play-by-play", "raw_po", "raw_rs"]:
        src_folder = os.path.join(RAW_BASE, sub)
        dst_folder = os.path.join(CLEAN_BASE, sub.replace("raw_", ""))
        ensure_dir(dst_folder)

        for file in os.listdir(src_folder):
            if file.startswith("df_") and file.endswith(".csv"):
                # df_rs_2025.csv → rs_2025.csv
                new_name = file.replace("df_", "")
                copy_and_rename(os.path.join(src_folder, file), dst_folder, new_name)

    # --- 6. Teams Stats (split into subfolders) ---
    TEAM_MAP = {
        "raw_east_standing": "east_standing",
        "raw_west_standing": "west_standing",
        "raw_team_adv_stats": "team_adv_stats",
        "raw_team_tot_stats": "team_tot_stats",
        "raw_team_pg_stats": "team_pg_stats",
        "raw_team_per_poss_stats": "team_per_poss_stats",
    }

    src_folder = os.path.join(RAW_BASE, "raw_teams_stats")
    for sub, clean_name in TEAM_MAP.items():
        dst_folder = os.path.join(CLEAN_BASE, clean_name)
        ensure_dir(dst_folder)

        for file in os.listdir(src_folder):
            if sub in file and file.endswith(".csv"):
                # raw_team_adv_stats_2025.csv → team_adv_stats_2025.csv
                year = file.split("_")[-1].replace(".csv", "")
                new_name = f"{clean_name}_{year}.csv"
                copy_and_rename(os.path.join(src_folder, file), dst_folder, new_name)

    print("\n🎉 Réorganisation terminée ! Tous les fichiers sont dans 'raw_data/'.")

if __name__ == "__main__":
    reorganize_raw()
