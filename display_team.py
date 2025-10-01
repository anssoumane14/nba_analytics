# check_team_mapping.py
import pandas as pd

# 🔧 Choisir saison et type
year = "2007"
season_type = "rs"   # ou "po"

file_path = f"processed_data_step2/{season_type}/{season_type}_{year}.csv"

# Charger
df = pd.read_csv(file_path, encoding="utf-8-sig")

print(f"📂 Vérification fichier : {file_path}")
print(f"Nombre de lignes : {len(df)}")

# Afficher équipes distinctes
if "TEAM" in df.columns:
    teams = sorted(df["TEAM"].dropna().unique())
    print("📑 Distinct TEAM values :")
    for t in teams:
        print("-", t)
else:
    print("❌ Colonne TEAM non trouvée")
