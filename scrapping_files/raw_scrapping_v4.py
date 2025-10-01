import time
from functions import run_team_batch

if __name__ == "__main__":
    batches = [
        (2025, 2016),
        (2015, 2006),
        (2005, 1996),
        (1995, 1986),
        (1985, 1976),
    ]

    for start, end in batches:
        print(f"\n🚀 Team stats batch {start}-{end} ...")
        run_team_batch(start, end)
        print(f"\n😴 Sleeping 10min before next batch...\n")
        time.sleep(300)  # 5 min pause between decades



