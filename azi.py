import pandas as pd

# -------------------------------------
# Scrape Player Salaries (current table)
# -------------------------------------
def scrape_salaries() -> pd.DataFrame:
    """
    Scrape current NBA player contracts from Basketball Reference.
    Table is updated each year automatically.
    
    Returns:
        pd.DataFrame: Salary data with columns for each season.
    """
    url = "https://www.basketball-reference.com/contracts/players.html"
    df = pd.read_html(url, header=0)[0]

    # Clean column names
    df.columns = [col.strip() for col in df.columns]

    return df
