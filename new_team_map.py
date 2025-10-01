# new_team_map.py
import pandas as pd

# --- dictionnaire complet avec anciennes équipes ---
nba_teams_dict = {
    # Actuelles
    "ATL": "Atlanta Hawks", "BOS": "Boston Celtics", "BRK": "Brooklyn Nets",
    "CHI": "Chicago Bulls", "CHO": "Charlotte Hornets", "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets", "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
    "LAC": "Los Angeles Clippers", "LAL": "Los Angeles Lakers", "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat", "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans", "NYK": "New York Knicks", "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic", "PHI": "Philadelphia 76ers", "PHO": "Phoenix Suns",
    "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings", "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors", "UTA": "Utah Jazz", "WAS": "Washington Wizards",

    # Historiques
    "NJN": "New Jersey Nets", "NYN": "New York Nets", "CHA": "Charlotte Bobcats",
    "CHH": "Charlotte Hornets (1988–2002)", "NOH": "New Orleans Hornets",
    "NOK": "New Orleans/Oklahoma City Hornets", "NOJ": "New Orleans Jazz",
    "SEA": "Seattle SuperSonics", "VAN": "Vancouver Grizzlies",
    "BUF": "Buffalo Braves", "KCK": "Kansas City Kings", "SDC": "San Diego Clippers",
    "WSB": "Washington Bullets",
}

def fix_team_names(df: pd.DataFrame) -> pd.DataFrame:
    """Corrige TEAM en utilisant TM quand TEAM == 'Unknown'"""
    if "TEAM" not in df.columns:
        return df

    if "TM" in df.columns:
        df["TEAM"] = df.apply(
            lambda row: nba_teams_dict.get(row["TM"], row["TEAM"])
            if row["TEAM"] == "Unknown" else row["TEAM"],
            axis=1
        )
    return df


if __name__ == "__main__":
    # Charger les datasets
    files = [
        "flat_table/flat_rs_player_final_stats.csv",
        "flat_table/flat_po_player_final_stats.csv",
    ]

    for file in files:
        print(f"🔄 Processing {file} ...")
        df = pd.read_csv(file, encoding="utf-8-sig")
        df = fix_team_names(df)
        df.to_csv(file, index=False, encoding="utf-8-sig")
        print(f"✅ Updated and saved {file}")
        print("🏀 Distinct TEAM after mapping:", sorted(df["TEAM"].dropna().unique()))
        print("-" * 60)
