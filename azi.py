import streamlit as st
import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd

st.title("🏀 NBA Honors 2025 (All-NBA, All-Defensive, All-Rookie, All-Star)")

url = "https://www.basketball-reference.com/leagues/NBA_2025.html"
headers = {"User-Agent": "Mozilla/5.0"}

res = requests.get(url, headers=headers, timeout=30)
res.raise_for_status()
res.encoding = "utf-8"
soup = BeautifulSoup(res.text, "html.parser")

def parse_section(section_id: str, grid_id: str, expected_cols=None):
    """Extrait une section (All-NBA, All-Defensive, etc.) en DataFrame"""
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
        players = [a.get_text(strip=True) for a in table.find_all("a") if a.get("href", "").startswith("/players/")]
        teams[name] = players

    if not teams:
        return None

    # Construire DataFrame
    ordered = list(teams.keys())
    if expected_cols:
        ordered = [c for c in expected_cols if c in teams] + [k for k in teams if k not in expected_cols]

    max_len = max(len(teams[k]) for k in ordered)
    data = {k: teams.get(k, []) + [""] * (max_len - len(teams.get(k, []))) for k in ordered}
    return pd.DataFrame(data)

# --- Scraper et afficher chaque tableau ---
sections = {
    "All-NBA Teams": ("all_all-nba", "div_all-nba", ["1st Team", "2nd Team", "3rd Team"]),
    "All-Defensive Teams": ("all_all-defensive", "div_all-defensive", ["1st Team", "2nd Team"]),
    "All-Rookie Teams": ("all_all-rookie", "div_all-rookie", ["1st Team", "2nd Team"]),
    "All-Star Rosters": ("all_all_star_game_rosters", "div_all_star_game_rosters", None),
}

for title, (section_id, grid_id, cols) in sections.items():
    df = parse_section(section_id, grid_id, cols)
    st.subheader(title)
    if df is not None:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning(f"⚠️ Pas de données trouvées pour {title}")
