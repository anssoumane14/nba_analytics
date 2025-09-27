import pandas as pd
import os
import time
import random
from functions import scrape_regular_season, scrape_playoffs, scrape_awards,run_batch,concat_raw_data



# -------------------------------
# Run concat for each dataset
# -------------------------------
concat_raw_data("raw_data_bball_ref/raw_rs", "flat_rs_all.csv")
concat_raw_data("raw_data_bball_ref/raw_po", "flat_po_all.csv")
concat_raw_data("raw_data_bball_ref/raw_award", "flat_award_all.csv")
