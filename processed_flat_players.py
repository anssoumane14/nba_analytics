# process_flat_players.py
import pandas as pd
import os

# -------------------------------------
# Utility Functions
# -------------------------------------
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
        'GSW': 'Golden State Warriors', 'PHI': 'Philadelphia 76ers', 'DEN': 'Denver Nuggets',
        'HOU': 'Houston Rockets', 'BOS': 'Boston Celtics', 'MIL': 'Milwaukee Bucks',
        'DAL': 'Dallas Mavericks', 'PHO': 'Phoenix Suns', 'NYK': 'New York Knicks',
        'LAL': 'Los Angeles Lakers', 'LAC': 'Los Angeles Clippers', 'SAC': 'Sacramento Kings',
        'CLE': 'Cleveland Cavaliers', 'UTA': 'Utah Jazz', 'ATL': 'Atlanta Hawks',
        'MIN': 'Minnesota Timberwolves', 'IND': 'Indiana Pacers', 'NOP': 'New Orleans Pelicans',
        'MEM': 'Memphis Grizzlies', 'TOR': 'Toronto Raptors', 'ORL': 'Orlando Magic',
        'DET': 'Detroit Pistons', 'OKC': 'Oklahoma City Thunder', 'BRK': 'Brooklyn Nets',
        'CHO': 'Charlotte Hornets', 'MIA': 'Miami Heat', 'SAS': 'San Antonio Spurs',
        'POR': 'Portland Trail Blazers', 'WAS': 'Washington Wizards', 'CHI': 'Chicago Bulls'
    }

    if abbr_col not in df.columns:
        return df

    df["TEAM"] = df[abbr_col].apply(lambda abv: nba_teams_dict.get(abv, "Unknown"))
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
