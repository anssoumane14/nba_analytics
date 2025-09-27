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
        time.sleep(random.randint(60,65))
