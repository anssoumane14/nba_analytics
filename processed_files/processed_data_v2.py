import os
import shutil
import pandas as pd
from functions import process_folder, clean_awards

if __name__ == "__main__":
    RAW_BASE = "raw_data_bball_ref"
    PROC_BASE = "processed_data"

    # 🔄 Supprimer le dossier processed_data si déjà existant
    if os.path.exists(PROC_BASE):
        shutil.rmtree(PROC_BASE)
    os.makedirs(PROC_BASE, exist_ok=True)

    # --- TEAM STATS ---
    process_folder(
        f"{RAW_BASE}/raw_teams_stats",
        f"{PROC_BASE}/teams_stats"
    )

    # --- PLAYER STATS (RS, PO, Advanced, Per Poss, PBP) ---
    player_folders = [
        "raw_rs",
        "raw_po",
        "raw_advanced",
        "raw_per_poss",
        "raw_play-by-play",
    ]
    for sub in player_folders:
        process_folder(
            os.path.join(RAW_BASE, sub),
            os.path.join(PROC_BASE, sub.replace("raw_", ""))
        )

    # --- AWARDS ---
    raw_award = os.path.join(RAW_BASE, "raw_award")
    proc_award = os.path.join(PROC_BASE, "awards")
    os.makedirs(proc_award, exist_ok=True)

    for file in os.listdir(raw_award):
        if not file.endswith(".csv"):
            continue
        df = pd.read_csv(os.path.join(raw_award, file), encoding="utf-8-sig")
        df = clean_awards(df)

        out_path = os.path.join(proc_award, f"clean_{file}")
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"✅ Awards cleaned: {out_path}")

    # --- HONORS (All-NBA / Def / Rookie / Star) ---
    honor_folders = [
        "raw_all_nba_teams",
        "raw_all_def_teams",
        "raw_all_rookie_teams",
        "raw_all_star_teams",
    ]
    for sub in honor_folders:
        process_folder(
            os.path.join(RAW_BASE, sub),
            os.path.join(PROC_BASE, sub.replace("raw_", ""))
        )

    print("\n🎉 Processing terminé, processed_data est prêt !")
