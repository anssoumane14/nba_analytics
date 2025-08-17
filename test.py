
import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_excel("data/df_team_playoff_stats_pg.xlsx")
st.set_page_config(layout="wide")

st.dataframe(df)