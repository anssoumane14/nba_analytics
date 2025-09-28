import time
from functions import run_batch_v2

if __name__ == "__main__":
    # Define decades
    batches = [
        #(2025, 2016),
        #(2015, 2006),
        #(2005, 1996),
        (1995, 1986),
        (1985, 1976),
    ]

    # Loop through decades
    for start, end in batches:
        print(f"\n🚀 Starting batch {start}-{end} ...\n")
        
        run_batch_v2(start, end, table_types=["per_poss", "advanced", "play-by-play"])
        
        print(f"\n😴 Sleeping between batches to avoid block ...\n")
        time.sleep(600)  # 10 minutes pause
