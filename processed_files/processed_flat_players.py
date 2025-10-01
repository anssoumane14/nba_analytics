import pandas as pd
import os
import re

# -------------------------------------
# Utility Functions
# -------------------------------------
def clean_player_names(df: pd.DataFrame) -> pd.DataFrame:
    if "PLAYER" in df.columns:
        # Enlève * et espaces superflus
        df["PLAYER"] = df["PLAYER"].astype(str).apply(lambda x: re.sub(r"\*", "", x).strip())
    return df


def compute_per_game(df: pd.DataFrame) -> pd.DataFrame:
    if "G" not in df.columns:
        return df
    per_game_df = df.copy()

    exclude_cols = {
        "RK", "PLAYER", "TEAM", "TM", "POS", "AGE", "SEASON", "SEASON_TYPE",
        "AWARDS", "TRP-DBL", "FG%", "3P%", "2P%", "FT%", "EFG%", "G", "GS"
    }

    for col in df.columns:
        if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col]):
            per_game_df[col + "_PG"] = (df[col] / df["G"]).round(1)

    return per_game_df


def map_team_names(df: pd.DataFrame, abbr_col: str = "TM") -> pd.DataFrame:
    nba_teams_dict = {
        # Équipes actuelles
        "ATL": "Atlanta Hawks",
        "BOS": "Boston Celtics",
        "BRK": "Brooklyn Nets",
        "CHI": "Chicago Bulls",
        "CHO": "Charlotte Hornets",  # version actuelle (depuis 2014)
        "CLE": "Cleveland Cavaliers",
        "DAL": "Dallas Mavericks",
        "DEN": "Denver Nuggets",
        "DET": "Detroit Pistons",
        "GSW": "Golden State Warriors",
        "HOU": "Houston Rockets",
        "IND": "Indiana Pacers",
        "LAC": "Los Angeles Clippers",
        "LAL": "Los Angeles Lakers",
        "MEM": "Memphis Grizzlies",
        "MIA": "Miami Heat",
        "MIL": "Milwaukee Bucks",
        "MIN": "Minnesota Timberwolves",
        "NOP": "New Orleans Pelicans",
        "NYK": "New York Knicks",
        "OKC": "Oklahoma City Thunder",
        "ORL": "Orlando Magic",
        "PHI": "Philadelphia 76ers",
        "PHO": "Phoenix Suns",
        "POR": "Portland Trail Blazers",
        "SAC": "Sacramento Kings",
        "SAS": "San Antonio Spurs",
        "TOR": "Toronto Raptors",
        "UTA": "Utah Jazz",
        "WAS": "Washington Wizards",

        # Anciennes équipes / renommages
        "NJN": "New Jersey Nets",
        "NYN": "New York Nets",
        "CHA": "Charlotte Bobcats",
        "CHH": "Charlotte Hornets",
        "NOH": "New Orleans Hornets",
        "NOK": "New Orleans/Oklahoma City Hornets",
        "NOJ": "New Orleans Jazz",
        "SEA": "Seattle SuperSonics",
        "VAN": "Vancouver Grizzlies",
        "BUF": "Buffalo Braves",
        "KCK": "Kansas City Kings",
        "SDC": "San Diego Clippers",
        "WSB": "Washington Bullets",
    }

    if abbr_col not in df.columns:
        return df

    df["TEAM"] = df[abbr_col].apply(lambda abv: nba_teams_dict.get(abv, "Unknown"))
    return df


def normalize_season_column(df: pd.DataFrame, is_playoff: bool) -> pd.DataFrame:
    if "SEASON" not in df.columns:
        return df

    df["SEASON"] = df["SEASON"].astype(str)

    if is_playoff:
        # Exemple : "2001" → "2000-01"
        df["SEASON"] = df["SEASON"].apply(
            lambda x: f"{int(x)-1}-{str(x)[-2:]}" if len(x) == 4 else x
        )

    return df

# -------------------------------------
# Processing Function
# -------------------------------------
def process_file(file_type: str):
    """
    file_type = 'rs' (regular season) or 'po' (playoffs)
    """
    input_path = f"flat_table/flat_{file_type}_player.csv"
    output_path = f"flat_table/flat_{file_type}_player_final.csv"

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"❌ File not found: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8-sig")

    # Standardize PLAYER col
    if "PLAYER" not in df.columns and "Player" in df.columns:
        df.rename(columns={"Player": "PLAYER"}, inplace=True)

    # Nettoyer les noms des joueurs
    df = clean_player_names(df)

    # Normalize SEASON column
    df = normalize_season_column(df, is_playoff=(file_type == "po"))

    # Handle TEAM names
    if "TM" in df.columns:  # playoffs
        df = map_team_names(df, "TM")
    elif "TEAM" in df.columns:  # regular season
        df = map_team_names(df, "TEAM")

    # Compute per-game stats
    df = compute_per_game(df)

    # Drop RK if exists
    if "RK" in df.columns:
        df.drop(columns=["RK"], inplace=True)

    # Save processed file
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ Processed {input_path} → {output_path}")


# -------------------------------------
# Main
# -------------------------------------
if __name__ == "__main__":
    process_file("rs")  # regular season
    process_file("po")  # playoffs
