import os
import pandas as pd

# -------------------------------
# General Helpers
# -------------------------------
def concat_raw_data(folder: str):
    """Concatène tous les CSV d'un dossier avec schéma aligné sur le plus récent."""
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    files = sorted(files)
    if not files:
        return pd.DataFrame()

    dfs = []
    ref_path = os.path.join(folder, files[-1])
    ref_df = pd.read_csv(ref_path, encoding="utf-8-sig")
    ref_columns = ref_df.columns.tolist()

    for f in files:
        path = os.path.join(folder, f)
        df = pd.read_csv(path, encoding="utf-8-sig")
        df = df.reindex(columns=ref_columns, fill_value=pd.NA)
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


# -------------------------------
# Flats builder
# -------------------------------
if __name__ == "__main__":
    PROC_BASE = "processed_data"
    FLAT_BASE = "flat_table"
    os.makedirs(FLAT_BASE, exist_ok=True)

    # --- Player stats ---
    player_folders = {
        "flat_rs_player": "rs",
        "flat_po_player": "po",
        "flat_advanced_player": "advanced",
        "flat_per_poss_player": "per_poss",
        "flat_pbp_player": "play-by-play",
    }

    for flat_name, folder in player_folders.items():
        df = concat_raw_data(f"{PROC_BASE}/{folder}")
        if df.empty:
            print(f"⚠️ {flat_name} skipped (no data)")
            continue
        out_path = f"{FLAT_BASE}/{flat_name}.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"✅ {flat_name} → {out_path} ({len(df)} lignes)")

    # --- Honors ---
    honor_folders = {
        "flat_all_nba_teams": "all_nba_teams",
        "flat_all_def_teams": "all_def_teams",
        "flat_all_rookie_teams": "all_rookie_teams",
        # pas de flat pour all_star_teams
    }

    for flat_name, folder in honor_folders.items():
        df = concat_raw_data(f"{PROC_BASE}/{folder}")
        if df.empty:
            print(f"⚠️ {flat_name} skipped (no data)")
            continue
        out_path = f"{FLAT_BASE}/{flat_name}.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"✅ {flat_name} → {out_path} ({len(df)} lignes)")

    # --- Teams ---
    team_folders = {
        "flat_east_standing": "east_standing",
        "flat_west_standing": "west_standing",
        "flat_team_tot_stats": "team_tot_stats",
        "flat_team_pg_stats": "team_pg_stats",
        "flat_team_per_poss_stats": "team_per_poss_stats",
        "flat_team_adv_stats": "team_adv_stats",
    }

    for flat_name, folder in team_folders.items():
        df = concat_raw_data(f"{PROC_BASE}/{folder}")
        if df.empty:
            print(f"⚠️ {flat_name} skipped (no data)")
            continue
        out_path = f"{FLAT_BASE}/{flat_name}.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"✅ {flat_name} → {out_path} ({len(df)} lignes)")

    # --- Awards ---
    df = concat_raw_data(f"{PROC_BASE}/awards")
    if not df.empty:
        out_path = f"{FLAT_BASE}/flat_awards.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"✅ flat_awards → {out_path} ({len(df)} lignes)")
    else:
        print("⚠️ flat_awards skipped (no data)")
