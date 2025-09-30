import pandas as pd

def resolve_last_team(df: pd.DataFrame) -> pd.DataFrame:
    # Step 1: sort dataset by player, season, and row order
    df1 = df.sort_values(["PLAYER", "SEASON"]).reset_index(drop=True)

    # Step 2: keep only the last row per (PLAYER, SEASON)
    df2 = df1.drop_duplicates(subset=["PLAYER", "SEASON"], keep="last").copy()

    # Step 3: replace "Unknown" with the last valid team from df1
    for idx, row in df2.iterrows():
        if row["TEAM"] == "Unknown":
            # Get last row for this player-season from df1
            last_team = (
                df1[(df1["PLAYER"] == row["PLAYER"]) & (df1["SEASON"] == row["SEASON"])]
                .iloc[-1]["TEAM"]
            )
            df2.at[idx, "TEAM"] = last_team

    
        

    return df2


if __name__ == "__main__":
    for t in ["rs", "po"]:
        input_path = f"flat_table/flat_{t}_player_final.csv"
        output_path = f"flat_table/flat_{t}_player_final_stats.csv"

        df = pd.read_csv(input_path, encoding="utf-8-sig")
        df_clean = resolve_last_team(df)

        df_clean.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"✅ Processed {input_path} → {output_path}")
