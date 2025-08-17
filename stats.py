
import streamlit as st
import pandas as pd
import plotly.express as px
#py -m streamlit run test.py
st.set_page_config(layout="wide")
df_nba_players = pd.read_excel("data/df_nba_players.xlsx")



st.title("Statistics")

filtre = st.selectbox("Choisissez un filtre", ["Leaders", "Points (Top 30)"])