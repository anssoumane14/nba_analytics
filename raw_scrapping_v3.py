import os, time, random
import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment

from functions import run_honors_batch

if __name__ == "__main__":
    batches = [
        (2025, 2016),
        (2015, 2006),
        (2005, 1996),
        (1995, 1986),
        (1985, 1976),
    ]

    for start, end in batches:
        print(f"\n🚀 Honors batch {start}-{end} ...")
        run_honors_batch(start, end)
        print(f"\n😴 Sleeping 10min before next batch...\n")
        time.sleep(600)
