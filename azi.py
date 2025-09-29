import pandas as pd
import streamlit as st
# "raw_data_bball_ref/raw_advanced/df_advanced_po_2016.csv"
# "raw_data_bball_ref/raw_per_poss/df_per_poss_po_2016.csv"

df = pd.read_csv("raw_data_bball_ref/raw_play-by-play/df_play-by-play_po_2024.csv")

st.dataframe(df)