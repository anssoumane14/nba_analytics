# processed_data_step3.py
import os
import pandas as pd

# -------------------------------
# Helper: concatène fichiers step2
# -------------------------------
def concat_step2_data(folder: str):
    """Concatène tous les CSV d'un dossier avec schéma aligné sur le plus récent."""
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    files = sorted(files)
    if not files:
        return pd.DataFrame()

    dfs = []
    # On prend les colonnes du plus récent comme référence
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
# Build Flat Tables
# -------------------------------
if __name__ == "__main__":
    STEP2_BASE = "processed_data_step2"
    FLAT_BASE = "flat_table"
    os.makedirs(FLAT_BASE, exist_ok=True)

    player_folders = {
        "flat_rs_player": "rs",
        "flat_po_player": "po",
    }

    for flat_name, folder in player_folders.items():
        folder_path = f"{STEP2_BASE}/{folder}"
        if not os.path.exists(folder_path):
            print(f"⚠️ {folder_path} n'existe pas → ignoré")
            continue

        df = concat_step2_data(folder_path)
        if df.empty:
            print(f"⚠️ {flat_name} skipped (no data)")
            continue

        out_path = f"{FLAT_BASE}/{flat_name}.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"✅ {flat_name} → {out_path} ({len(df)} lignes)")
