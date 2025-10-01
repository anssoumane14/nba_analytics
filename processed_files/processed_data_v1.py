import pandas as pd
import os
from functions import (
    concat_raw_data, normalize_columns, compute_per_game,
    map_team_names, expand_awards, add_primary_key
)

# -------------------------------
# Load raw data
# -------------------------------
df_rs = concat_raw_data("raw_data_bball_ref/raw_rs")
df_po = concat_raw_data("raw_data_bball_ref/raw_po")

# -------------------------------
# Normalize column names
# -------------------------------
df_rs = normalize_columns(df_rs)
df_po = normalize_columns(df_po)

# -------------------------------
# Compute per-game stats
# -------------------------------
df_rs_pg = compute_per_game(df_rs)
df_po_pg = compute_per_game(df_po)

# -------------------------------
# TEAM mapping
# -------------------------------
# RS → rename TEAM → TM first (so schema matches playoffs)
df_rs_pg.rename(columns={"TEAM": "TM"}, inplace=True)
df_rs_pg = map_team_names(df_rs_pg, abbr_col="TM")

# PO → already has TM
df_po_pg = map_team_names(df_po_pg, abbr_col="TM")



# -------------------------------
# Add Primary Key
# -------------------------------
df_rs_pg = add_primary_key(df_rs_pg)   # uses TEAM (full name) internally
df_po_pg = add_primary_key(df_po_pg)



# -------------------------------
# Export to processed_data
# -------------------------------
os.makedirs("processed_data", exist_ok=True)

df_rs_pg.to_csv("processed_data/flat_rs.csv", index=False, encoding="utf-8-sig")
df_po_pg.to_csv("processed_data/flat_po.csv", index=False, encoding="utf-8-sig")

df_award = pd.read_csv("processed_data/flat_rs_all.csv", encoding = "utf-8-sig")
df_award.to_csv("processed_data/flat_award.csv", index=False, encoding="utf-8-sig")


print("\n💾 Exported:")
print(f"- Regular season → processed_data/flat_rs.csv ({len(df_rs_pg)} rows)")
print(f"- Playoffs       → processed_data/flat_po.csv ({len(df_po_pg)} rows)")
