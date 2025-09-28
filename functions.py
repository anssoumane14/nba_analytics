import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import html
import os
import time
import random

# -------------------------------------
# Scrape Awards
# -------------------------------------
def scrape_awards(year: int) -> pd.DataFrame:
    """
    Scrape awards & leaders for a given NBA season from Basketball Reference.
    
    Args:
        year (int): Last year of the season (e.g., 2024 for the 2023-24 season).
    
    Returns:
        pd.DataFrame: Awards table with columns [id_award, Season, Award, Player, PPG, RPG, APG, WS].
    """
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}.html"
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract season in format YYYY-YY (e.g. "2023-24")
    season_title = soup.find("h1").get_text(strip=True)
    match = re.search(r"\d{4}-\d{2}", season_title)
    season = match.group(0) if match else str(year)

    # Parse awards section
    meta_div = soup.find("div", id="meta")
    award_lines = meta_div.find_all("p")

    records = []
    id_award = 1

    for line in award_lines:
        text = line.get_text(" ", strip=True)
        if ":" not in text:
            continue

        award, details = text.split(":", 1)
        award = award.strip()

        # Decode HTML entities (fix names like Jokić, Dončić, etc.)
        details = html.unescape(details.strip())

        # Extract player and stats
        match = re.match(r"(.+?) \((.*?)\)", details)
        if match:
            player = match.group(1).strip()
            stats = match.group(2).split("/")
        else:
            player = details.strip()
            stats = []

        # Initialize stat fields
        ppg, rpg, apg, ws = [np.nan]*4
        if award in ["Most Valuable Player", "Rookie of the Year"]:
            if len(stats) >= 3:
                ppg, rpg, apg = stats[:3]
        elif "PPG Leader" in award:
            ppg = stats[0]
        elif "RPG Leader" in award:
            rpg = stats[0]
        elif "APG Leader" in award:
            apg = stats[0]
        elif "WS Leader" in award:
            ws = stats[0]

        records.append([id_award, season, award, player, ppg, rpg, apg, ws])
        id_award += 1

    return pd.DataFrame(records, columns=["id_award","Season","Award","Name","PPG","RPG","APG","WS"])


# -------------------------------------
# Scrape Regular Season Player Totals
# -------------------------------------
def scrape_regular_season(year: int) -> pd.DataFrame:
    """
    Scrape regular season player totals for a given year.
    
    Args:
        year (int): Last year of the season (e.g., 2024 for the 2023-24 season).
    
    Returns:
        pd.DataFrame: Player totals with a Season column.
    """
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_totals.html"
    df = pd.read_html(url, header=0)[0]

    # Remove duplicate headers inside table
    df = df[df["Player"] != "Player"]

    # Add Season column (e.g., "2023-24")
    df["Season"] = f"{year-1}-{str(year)[-2:]}"
    df["Season_Type"] = "Regular Season"

    return df


# -------------------------------------
# Scrape Playoff Player Totals
# -------------------------------------
def scrape_playoffs(year: int) -> pd.DataFrame:
    """
    Scrape playoff player totals for a given year.
    
    Args:
        year (int): Last year of the season (e.g., 2024 for the 2023-24 season).
    
    Returns:
        pd.DataFrame: Playoff player totals with a Season column.
    """
    url = f"https://www.basketball-reference.com/playoffs/NBA_{year}_totals.html"
    df = pd.read_html(url, header=0)[0]

    # Remove duplicate headers inside table
    df = df[df["Player"] != "Player"]

    # Add Season column (e.g., "2023-24")
    df["Season"] = f"{year-1}-{str(year)[-2:]}"
    df["Season_Type"] = "Playoffs"

    return df




# -------------------------------------
# Batch Runner
# -------------------------------------
def run_batch(start_year, end_year):
    for year in range(start_year, end_year - 1, -1):
        print(f"⏳ Scraping season {year-1}-{str(year)[-2:]} ...")
        try:
            # Regular Season
            df_rs = scrape_regular_season(year)
            df_rs.to_csv(f"raw_data_bball_ref/raw_rs/df_rs_{year}.csv", index=False, encoding="utf-8-sig")

            # Playoffs
            df_po = scrape_playoffs(year)
            df_po.to_csv(f"raw_data_bball_ref/raw_po/df_po_{year}.csv", index=False, encoding="utf-8-sig")

            # Awards
            df_awards = scrape_awards(year)
            df_awards.to_csv(f"raw_data_bball_ref/raw_award/df_awards_{year}.csv", index=False, encoding="utf-8-sig")

            print(f"✅ Finished season {year-1}-{str(year)[-2:]}")

        except Exception as e:
            print(f"⚠️ Skipped {year} due to error: {e}")

        # Short random delay (5–12s) between requests
        time.sleep(random.randint(90,120))




# -------------------------------------
# Scrape Player Salaries (current table)
# -------------------------------------
def scrape_salaries() -> pd.DataFrame:
    """
    Scrape current NBA player contracts from Basketball Reference.
    Table is updated each year automatically.
    
    Returns:
        pd.DataFrame: Salary data with columns for each season.
    """
    url = "https://www.basketball-reference.com/contracts/players.html"
    df = pd.read_html(url, header=0)[0]

    # Clean column names
    df.columns = [col.strip() for col in df.columns]

    return df





# -------------------------------------
# Concat raw data
# -------------------------------------

def concat_raw_data(folder: str):
    """
    Concatenate all CSVs in a folder into one big file.
    Keeps column order from the latest file.
    Missing columns are filled with NaN.
    Returns a dataframe (not saved to disk).
    """
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    files = sorted(files)  # chronological order

    if not files:
        print(f"⚠️ No files found in {folder}")
        return pd.DataFrame()

    dfs = []
    # Reference schema = last file (latest season with most columns)
    ref_path = os.path.join(folder, files[-1])
    ref_df = pd.read_csv(ref_path, encoding="utf-8-sig")
    ref_columns = ref_df.columns.tolist()

    for f in files:
        path = os.path.join(folder, f)
        df = pd.read_csv(path, encoding="utf-8-sig")
        # Align columns with reference schema
        df = df.reindex(columns=ref_columns, fill_value=pd.NA)
        dfs.append(df)

    # Concat all with consistent schema
    df_all = pd.concat(dfs, ignore_index=True)
    return df_all



# -------------------------------------
# Processing: normalize columns
# -------------------------------------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names:
    - Uppercase
    - Strip spaces
    """
    df.columns = [col.upper().strip() for col in df.columns]
    return df



# -------------------------------------
# Processing: compute per-game stats
# -------------------------------------
def compute_per_game(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-game stats for numeric columns.
    Excludes percentage columns.
    Adds suffix '_PG'.
    """
    if "G" not in df.columns:
        print("⚠️ 'G' (games) column missing, cannot compute per-game stats.")
        return df

    per_game_df = df.copy()
    exclude_cols = {"RK", "PLAYER", "TEAM", "TM", "POS", "AGE", "SEASON", "SEASON_TYPE", 
                    "AWARDS", "TRP-DBL", "FG%", "3P%", "2P%", "FT%", "EFG%","G","GS"}

    # Loop through columns
    for col in df.columns:
        if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col]):
            per_game_df[col + "_PG"] = (df[col] / df["G"]).round(1)

    return per_game_df



# -------------------------------------
# Processing: map team abbreviations to full names
# -------------------------------------
def map_team_names(df: pd.DataFrame, abbr_col: str = "TM") -> pd.DataFrame:
    """
    Add a full TEAM name column based on abbreviation column.
    - abbr_col: column containing team abbreviations (default = 'TM')
    - Adds new column 'TEAM' with full name.
    """
    nba_teams_dict = {
        'GSW': 'Golden State Warriors',
        'PHI': 'Philadelphia 76ers',
        'DEN': 'Denver Nuggets',
        'HOU': 'Houston Rockets',
        'BOS': 'Boston Celtics',
        'MIL': 'Milwaukee Bucks',
        'DAL': 'Dallas Mavericks',
        'PHO': 'Phoenix Suns',
        'NYK': 'New York Knicks',
        'LAL': 'Los Angeles Lakers',
        'LAC': 'Los Angeles Clippers',
        'SAC': 'Sacramento Kings',
        'CLE': 'Cleveland Cavaliers',
        'UTA': 'Utah Jazz',
        'ATL': 'Atlanta Hawks',
        'MIN': 'Minnesota Timberwolves',
        'IND': 'Indiana Pacers',
        'NOP': 'New Orleans Pelicans',
        'MEM': 'Memphis Grizzlies',
        'TOR': 'Toronto Raptors',
        'ORL': 'Orlando Magic',
        'DET': 'Detroit Pistons',
        'OKC': 'Oklahoma City Thunder',
        'BRK': 'Brooklyn Nets',
        'CHO': 'Charlotte Hornets',
        'MIA': 'Miami Heat',
        'SAS': 'San Antonio Spurs',
        'POR': 'Portland Trail Blazers',
        'WAS': 'Washington Wizards',
        'CHI': 'Chicago Bulls'
    }

    df = df.copy()
    if abbr_col not in df.columns:
        print(f"⚠️ Column {abbr_col} not found in dataframe.")
        return df

    df["TEAM"] = df[abbr_col].apply(lambda abv: nba_teams_dict.get(abv, "Unknown"))
    return df





# -------------------------------------
# Processing: expand AWARDS column
# -------------------------------------
def expand_awards(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand AWARDS column into multiple columns.
    Example: "MVP-8,AS,NBA2" → MVP=8, AS=1, NBA2=1
    """
    if "AWARDS" not in df.columns:
        print("⚠️ 'AWARDS' column not found, skipping expansion.")
        return df

    df_expanded = df.copy()

    all_awards = set()

    # First pass: collect all possible award types
    for raw in df_expanded["AWARDS"].dropna():
        parts = str(raw).split(",")
        for part in parts:
            key = part.split("-")[0]  # MVP-8 → MVP
            all_awards.add(key)

    # Add new columns initialized to 0
    for award in all_awards:
        df_expanded[award] = 0

    # Second pass: fill values
    for idx, raw in df_expanded["AWARDS"].dropna().items():
        parts = str(raw).split(",")
        for part in parts:
            if "-" in part:
                key, val = part.split("-", 1)
                df_expanded.at[idx, key] = int(val)
            else:
                df_expanded.at[idx, part] = 1

    return df_expanded




# -------------------------------------
# Add primary key (int) based on season + player + team + position
# -------------------------------------
def add_primary_key(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a reproducible integer primary key for each player-season-team-position.
    """
    # Build a unique string key
    df["PK_KEY"] = (
        df["SEASON"].astype(str) + "_" +
        df["PLAYER"].str.upper() + "_" +
        df["TEAM"].str.upper() + "_" +
        df["POS"].str.upper()
    )

    # Factorize to get unique int IDs
    df["PLAYER_ID"] = df["PK_KEY"].factorize()[0] + 1

    # Drop helper column if not needed
    #df.drop(columns=["PK_KEY"], inplace=True)

    return df



def scrape_table(year: int, table_type: str, playoffs: bool = False) -> pd.DataFrame:
    if playoffs:
        url = f"https://www.basketball-reference.com/playoffs/NBA_{year}_{table_type}.html"
        season_type = "Playoffs"
    else:
        url = f"https://www.basketball-reference.com/leagues/NBA_{year}_{table_type}.html"
        season_type = "Regular Season"

    try:
        df = pd.read_html(url, header=0)[0]
    except ValueError:
        print(f"⚠️ Pas de table trouvée (empty) pour {year} - {table_type}")
        return pd.DataFrame()
    except Exception as e:
        print(f"⚠️ Erreur pour {year} - {table_type}: {e}")
        return pd.DataFrame()

    # Supprimer headers répétés
    if "Player" in df.columns:
        df = df[df["Player"] != "Player"]

    df["Season"] = f"{year-1}-{str(year)[-2:]}"
    df["Season_Type"] = season_type

    return df


def run_batch_v2(year_start: int, year_end: int, table_types=None):
    """
    Scraper plusieurs saisons et plusieurs types de tables avec reprise automatique.
    
    Args:
        year_start (int): ex: 2025
        year_end (int): ex: 1976
        table_types (list): ex: ["totals", "per_poss", "advanced", "play-by-play", "shooting"]
    """
    if table_types is None:
        table_types = ["per_poss", "advanced", "play-by-play"]

    for year in range(year_start, year_end - 1, -1):
        print(f"\n🚀 Saison {year-1}-{str(year)[-2:]} ...")

        for table in table_types:
            for playoffs in [False, True]:
                folder = f"raw_data_bball_ref/raw_{table}"
                os.makedirs(folder, exist_ok=True)

                playoff_suffix = "_po" if playoffs else "_rs"
                path = f"{folder}/df_{table}{playoff_suffix}_{year}.csv"

                # ✅ Skip if file already exists
                if os.path.exists(path):
                    print(f"⏩ Déjà existant : {path}, on saute.")
                    continue

                df = scrape_table(year, table, playoffs)

                if df.empty:
                    continue

                df.to_csv(path, index=False, encoding="utf-8-sig")
                print(f"✅ {table} ({'Playoffs' if playoffs else 'RS'}) {year} → {len(df)} lignes")

        # Pause aléatoire pour éviter le blocage
        time.sleep(random.randint(60, 90))

    print("\n🎉 Batch terminé !")
