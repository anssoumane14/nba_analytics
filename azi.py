
# Create an in-memory DuckDB connection
con = db.connect()

# Make pandas DataFrames visible to SQL
con.register("reg", df_reg)
con.register("po", df_po)

# Now: run SQL!
tab = con.execute("""
    SELECT PLAYER_NAME, POSITION,TEAM_ABBREVIATION, 
    FROM reg
    WHERE POSITION = 'G-F' OR POSITION = 'F-G'
    LIMIT 1000
""").df()  # .df() returns a pandas DataFrame

st.dataframe(tab)
print(tab)