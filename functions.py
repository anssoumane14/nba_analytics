import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
import re
import numpy as np
import html
import os
import time
import random
import streamlit as st
# -------------------------------------
# Scrape Awards
# -------------------------------------
def scrape_awards(year: int) -> pd.DataFrame:
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}.html"
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    season_title = soup.find("h1").get_text(strip=True)
    match = re.search(r"\d{4}-\d{2}", season_title)
    season = match.group(0) if match else str(year)

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
        details = html.unescape(details.strip())

        match = re.match(r"(.+?) \((.*?)\)", details)
        if match:
            player = match.group(1).strip()
            stats = match.group(2).split("/")
        else:
            player = details.strip()
            stats = []

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
# Scrape Player Totals
# -------------------------------------
def scrape_regular_season(year: int) -> pd.DataFrame:
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_totals.html"
    df = pd.read_html(url, header=0)[0]
    df = df[df["Player"] != "Player"]
    df["Season"] = f"{year-1}-{str(year)[-2:]}"
    df["Season_Type"] = "Regular Season"
    return df

def scrape_playoffs(year: int) -> pd.DataFrame:
    url = f"https://www.basketball-reference.com/playoffs/NBA_{year}_totals.html"
    df = pd.read_html(url, header=0)[0]
    df = df[df["Player"] != "Player"]
    df["Season"] = f"{year-1}-{str(year)[-2:]}"
    df["Season_Type"] = "Playoffs"
    return df


# -------------------------------------
# Batch Runner (RS + PO + Awards)
# -------------------------------------
def run_batch(start_year, end_year):
    for year in range(start_year, end_year - 1, -1):
        print(f"⏳ Scraping season {year-1}-{str(year)[-2:]} ...")
        try:
            os.makedirs("raw_data/rs", exist_ok=True)
            os.makedirs("raw_data/po", exist_ok=True)
            os.makedirs("raw_data/awards", exist_ok=True)

            df_rs = scrape_regular_season(year)
            df_rs.to_csv(f"raw_data/rs/rs_{year}.csv", index=False, encoding="utf-8-sig")

            df_po = scrape_playoffs(year)
            df_po.to_csv(f"raw_data/po/po_{year}.csv", index=False, encoding="utf-8-sig")

            df_awards = scrape_awards(year)
            df_awards.to_csv(f"raw_data/awards/awards_{year}.csv", index=False, encoding="utf-8-sig")

            print(f"✅ Finished season {year-1}-{str(year)[-2:]}")

        except Exception as e:
            print(f"⚠️ Skipped {year} due to error: {e}")

        time.sleep(random.randint(90,120))


# -------------------------------------
# General Helpers
# -------------------------------------
def concat_raw_data(folder: str):
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

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [col.upper().strip().replace(" ", "_") for col in df.columns]
    return df


# -------------------------------------
# Stats Processing
# -------------------------------------
def compute_per_game(df: pd.DataFrame) -> pd.DataFrame:
    if "G" not in df.columns:
        return df
    per_game_df = df.copy()
    exclude_cols = {"RK","PLAYER","TEAM","TM","POS","AGE","SEASON","SEASON_TYPE",
                    "AWARDS","TRP-DBL","FG%","3P%","2P%","FT%","EFG%","G","GS"}
    for col in df.columns:
        if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col]):
            per_game_df[col + "_PG"] = (df[col] / df["G"]).round(1)
    return per_game_df


# functions.py

import pandas as pd

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
        "NJN": "New Jersey Nets",     # devenu Brooklyn Nets (2012)
        "NYN": "New York Nets",       # ABA → NBA avant de devenir NJN
        "CHA": "Charlotte Bobcats",   # devenu Charlotte Hornets (2014)
        "CHH": "Charlotte Hornets",   # original (1988–2002) → devenu New Orleans
        "NOH": "New Orleans Hornets", # 2002–2013 avant Pelicans
        "NOK": "New Orleans/Oklahoma City Hornets", # 2005–2007 (Katrina)
        "NOJ": "New Orleans Jazz",    # 1974–1979 → Utah Jazz
        "SEA": "Seattle SuperSonics", # devenu OKC en 2008
        "VAN": "Vancouver Grizzlies", # devenu Memphis en 2001
        "BUF": "Buffalo Braves",      # devenu Los Angeles Clippers
        "KCK": "Kansas City Kings",   # devenu Sacramento en 1985
        "SDC": "San Diego Clippers",  # avant déménagement à Los Angeles
        "WSB": "Washington Bullets",  # renommé en Wizards (1997)
    }

    if abbr_col not in df.columns:
        return df

    df["TEAM"] = df[abbr_col].apply(lambda abv: nba_teams_dict.get(str(abv), "Unknown"))
    return df


def expand_awards(df: pd.DataFrame) -> pd.DataFrame:
    if "AWARDS" not in df.columns:
        return df
    df_expanded = df.copy()
    all_awards = set()
    for raw in df_expanded["AWARDS"].dropna():
        for part in str(raw).split(","):
            all_awards.add(part.split("-")[0])
    for award in all_awards:
        df_expanded[award] = 0
    for idx, raw in df_expanded["AWARDS"].dropna().items():
        for part in str(raw).split(","):
            if "-" in part:
                key, val = part.split("-", 1)
                df_expanded.at[idx, key] = int(val)
            else:
                df_expanded.at[idx, part] = 1
    return df_expanded

def add_primary_key(df: pd.DataFrame) -> pd.DataFrame:
    df["PK_KEY"] = (
        df["SEASON"].astype(str) + "_" +
        df["PLAYER"].str.upper() + "_" +
        df["TEAM"].str.upper() + "_" +
        df["POS"].str.upper()
    )
    df["PLAYER_ID"] = df["PK_KEY"].factorize()[0] + 1
    return df


# -------------------------------------
# HONORS Scraping (All-NBA, etc.)
# -------------------------------------
def scrape_honors(year: int):
    season_label = f"{year-1}-{str(year)[-2:]}"
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}.html"
    res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=30)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    def parse_section(section_id: str, grid_id: str, expected_cols=None):
        section = soup.find("div", id=section_id)
        if not section:
            return None
        comment = next((c for c in section.find_all(string=lambda x: isinstance(x, Comment))
                        if grid_id in c), None)
        if not comment:
            return None
        block = BeautifulSoup(comment, "html.parser")
        grid = block.find("div", id=grid_id)
        if not grid:
            return None
        teams = {}
        for table in grid.find_all("table"):
            caption = table.find("caption")
            name = caption.get_text(strip=True) if caption else "Team"
            players = [a.get_text(strip=True) for a in table.find_all("a")
                       if a.get("href", "").startswith("/players/")]
            teams[name] = players
        if not teams:
            return None
        ordered = list(teams.keys())
        if expected_cols:
            ordered = [c for c in expected_cols if c in teams] + [k for k in teams if k not in expected_cols]
        max_len = max(len(teams[k]) for k in ordered)
        data = {k: teams.get(k, []) + [""]*(max_len-len(teams.get(k, []))) for k in ordered}
        df = pd.DataFrame(data)
        df["season"] = season_label
        return df

    sections = {
        "all_nba_teams": ("all_all-nba","div_all-nba",["1st Team","2nd Team","3rd Team"]),
        "all_def_teams": ("all_all-defensive","div_all-defensive",["1st Team","2nd Team"]),
        "all_rookie_teams": ("all_all-rookie","div_all-rookie",["1st Team","2nd Team"]),
        "all_star_teams": ("all_all_star_game_rosters","div_all_star_game_rosters",None),
    }

    for name, (section_id, grid_id, cols) in sections.items():
        folder = f"raw_data/{name}"
        os.makedirs(folder, exist_ok=True)
        path = f"{folder}/{name}_{year}.csv"
        if os.path.exists(path):
            continue
        df = parse_section(section_id, grid_id, cols)
        if df is not None:
            df.to_csv(path, index=False, encoding="utf-8-sig")
            print(f"✅ Saved {path} ({len(df)} rows)")

def run_honors_batch(year_start: int, year_end: int):
    for year in range(year_start, year_end - 1, -1):
        try:
            scrape_honors(year)
        except Exception as e:
            print(f"⚠️ Failed {year}: {e}")
        time.sleep(random.randint(60, 90))


# -------------------------------------
# TEAM STATS Scraping
# -------------------------------------
TEAM_TABLE_MAP = {
    "east_standing": 0,
    "west_standing": 1,
    "team_tot_stats": 4,
    "team_pg_stats": 5,
    "team_per_poss_stats": 8,
    "team_adv_stats": 10,
}

def scrape_team_table(year: int, table_type: str) -> pd.DataFrame:
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}.html"
    try:
        tables = pd.read_html(url, header=0)
        idx = TEAM_TABLE_MAP.get(table_type)
        if idx is None or idx >= len(tables):
            return pd.DataFrame()
        df = tables[idx]
    except Exception:
        return pd.DataFrame()
    if "Team" in df.columns:
        df = df[df["Team"] != "Team"]
    df["Season"] = f"{year-1}-{str(year)[-2:]}"
    return df

def run_team_batch(year_start: int, year_end: int, table_types=None):
    if table_types is None:
        table_types = list(TEAM_TABLE_MAP.keys())
    for year in range(year_start, year_end - 1, -1):
        for table in table_types:
            folder = f"raw_data/{table}"
            os.makedirs(folder, exist_ok=True)
            path = f"{folder}/{table}_{year}.csv"
            if os.path.exists(path):
                continue
            df = scrape_team_table(year, table)
            if not df.empty:
                df.to_csv(path, index=False, encoding="utf-8-sig")
                print(f"✅ {table} {year} → {len(df)} lignes")
        time.sleep(random.randint(60, 90))
    print("\n🎉 Batch team stats terminé !")


# -------------------------------------
# CLEANING HELPERS
# -------------------------------------
def clean_table(df: pd.DataFrame, table_type: str = None) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    df.columns = [str(c).upper().strip().replace(" ", "_") for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains("UNNAMED")]
    if any(df.iloc[0].astype(str).str.contains("TEAM", case=False, na=False)):
        df.columns = df.iloc[0].values
        df = df.drop(0).reset_index(drop=True)
    if table_type in TEAM_TABLE_MAP.keys():
        if "TEAM" in df.columns:
            df["PLAYOFF_TEAM"] = df["TEAM"].astype(str).str.contains(r"\*", na=False).astype(int)
            df["TEAM"] = df["TEAM"].str.replace(r"\*","",regex=True).str.strip()
    return df

def process_folder(raw_folder: str, out_folder: str):
    os.makedirs(out_folder, exist_ok=True)
    for file in os.listdir(raw_folder):
        if not file.endswith(".csv"):
            continue
        table_type = re.sub(r"_\d{4}.csv$", "", file)
        year_match = re.search(r"(\d{4})", file)
        year = year_match.group(1) if year_match else "UNKNOWN"
        path_in = os.path.join(raw_folder, file)
        df = pd.read_csv(path_in, encoding="utf-8-sig")
        df = clean_table(df, table_type)
        path_out = os.path.join(out_folder, f"clean_{file}")
        df.to_csv(path_out, index=False, encoding="utf-8-sig")
        print(f"✅ {file} → {path_out} ({len(df)} lignes)")

def clean_awards(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df.columns = [c.upper() for c in df.columns]
    return df

def clean_honors(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df.columns = [c.upper().replace(" ", "_") for c in df.columns]
    return df

def clean_player_stats(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df.columns = [c.upper().replace(" ", "_") for c in df.columns]
    return df
