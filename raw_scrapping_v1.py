import os
import time
import random
from functions import scrape_regular_season, scrape_playoffs, scrape_awards,run_batch

# python raw_scrapping.py

# Create folders if not exist
os.makedirs("raw_data_bball_ref/raw_rs", exist_ok=True)
os.makedirs("raw_data_bball_ref/raw_po", exist_ok=True)
os.makedirs("raw_data_bball_ref/raw_award", exist_ok=True)

# -------------------------------
# Scrape in batches
# -------------------------------
#batches = [(2025, 2016), (2015, 2006), (2005, 1996), (1995, 1986), (1985, 1976)] # it's already good for 2025-2026, i created the function run_batche because to many requests were sent
#⚠️ Skipped 2015 due to error: HTTP Error 429: Too Many Requests
#⏳ Scraping season 2013-14 ...

batches = [(2015, 2006), (2005, 1996), (1995, 1986), (1985, 1976)]

for start, end in batches:
    print(f"\n🚀 Starting batch {start}-{end} ...\n")
    run_batch(start, end)

    print(f"😴 Sleeping between batches to avoid block ...")
    time.sleep(600)  # 10 min pause between batches
