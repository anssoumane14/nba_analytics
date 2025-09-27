import os
from functions import scrape_salaries

# Create folder if not exist
os.makedirs("raw_data_bball_ref/raw_salary", exist_ok=True)

# Scrape salaries
df_salary = scrape_salaries()
# first column is 2025-26
df_salary.to_csv("raw_data_bball_ref/raw_salary/df_salary_2026.csv", index=False, encoding="utf-8-sig")

print("✅ Salary data saved!")
