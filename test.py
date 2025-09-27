import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import html
import streamlit as st
from functions import scrape_regular_season, scrape_playoffs,scrape_awards

import os
from functions import scrape_regular_season, scrape_playoffs, scrape_awards

# Ensure folders exist
os.makedirs("raw_data_bball_ref/df_rs", exist_ok=True)
os.makedirs("raw_data_bball_ref/df_po", exist_ok=True)
os.makedirs("raw_data_bball_ref/df_award", exist_ok=True)

# Example: scrape only 2024 season
year = 2024

# Regular Season
df_rs = scrape_regular_season(year)
df_rs.to_csv(f"raw_data_bball_ref/df_rs/df_rs_{year}.csv", index=False, encoding="utf-8-sig")

# Playoffs
df_po = scrape_playoffs(year)
df_po.to_csv(f"raw_data_bball_ref/df_po/df_po_{year}.csv", index=False, encoding="utf-8-sig")

# Awards
df_awards = scrape_awards(year)
df_awards.to_csv(f"raw_data_bball_ref/df_award/df_awards_{year}.csv", index=False, encoding="utf-8-sig")

print("✅ Data scraped and saved for season", year)
