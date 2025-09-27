import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import streamlit as st
import numpy as np
import html  # to decode HTML entities




# if will a loop from 2025 to 1976
# one season 
url = "https://www.basketball-reference.com/leagues/NBA_2024_totals.html"
df_rs =  pd.read_html(url, header=0)[0]
df_po = pd.read_html(url, header=0)[1]


# then we need to stored by adding the column of season for example 2023-2024 tell if forgot something
# then we export in csv in the folder : raw_data_bball_ref
# be careful with then name of data i want something harmonized : df_rs_2023_2024, df_po_2023_2024
# so when i'll concat the data it will be easier , hors maybe you have a better naming like only df_rs_2024
# no need to display
st.dataframe(df_rs)
st.dataframe(df_po)
# i think we will need to create function
# as you know i dont want to get reject by bball

# i also this kind of title : its better
# -------------------------------------
# DATAFRAME REGULAR SEASON / PLAYOFF
# -------------------------------------



# -------------------------------------
# AWARD
# -------------------------------------

url = "https://www.basketball-reference.com/leagues/NBA_2024.html"
response = requests.get(url)
response.encoding = "utf-8"  # force UTF-8

soup = BeautifulSoup(response.text, "html.parser")
# it will be probablya function 
# Find the awards/leader section
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

    # Decode HTML entities (fix Jokić, Dončić, etc.)
    details = html.unescape(details.strip())

    match = re.match(r"(.+?) \((.*?)\)", details)
    if match:
        player = match.group(1).strip()
        stats = match.group(2).split("/")
    else:
        player = details.strip()
        stats = []

    # Initialize values
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

    records.append([id_award, "2023-24", award, player, ppg, rpg, apg, ws])
    id_award += 1

# Build dataframe
df_awards = pd.DataFrame(records, columns=["id_award","Season","Award","Name","PPG","RPG","APG","WS"])

# Export to CSV with UTF-8 for Excel compatibility
df_awards.to_csv("test_award_v1.csv", index=False, encoding="utf-8-sig")

st.dataframe(df_awards)


