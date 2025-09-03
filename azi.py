# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="NBA Dashboard", layout="wide")

# -------------------------------
# Define Icon Paths as Variables
# -------------------------------
ICON_BASE_PATH = "icons/" # Base path to your icons folder

# Define individual icon paths
HOME_ICON = f"{ICON_BASE_PATH}home.png"
TEAM_ICON = f"{ICON_BASE_PATH}team.png"
STATISTICS_ICON = f"{ICON_BASE_PATH}statistics.png"
HISTORIC_ICON = f"{ICON_BASE_PATH}historic.png"
TRADE_MACHINE_ICON = f"{ICON_BASE_PATH}trade1.png"

# -------------------------------
# Show navbar with downloaded icons
# -------------------------------

# Create columns for your navigation items
c1, c2, c3, c4, c5 = st.columns(5)

# Home Link
with c1:
    st.image(HOME_ICON, width=30)
    if st.button("Home", key="nav_home_btn"):
        st.switch_page("home")

# Team Link
with c2:
    st.image(TEAM_ICON, width=30)
    if st.button("Team", key="nav_team_btn"):
        st.switch_page("pages/1_Team")

# Statistics Link
with c3:
    st.image(STATISTICS_ICON, width=30)
    if st.button("Statistics", key="nav_stats_btn"):
        st.switch_page("pages/2_Statistics")

# Historic Link
with c4:
    st.image(HISTORIC_ICON, width=30)
    if st.button("Historic", key="nav_historic_btn"):
        st.switch_page("pages/3_Champ_Historic")

# Trade Machine Link
with c5:
    st.image(TRADE_MACHINE_ICON, width=30)
    if st.button("Trade Machine", key="nav_trade_btn"):
        st.switch_page("pages/4_Trade_Machine")

# -------------------------------
# Title
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>🏀 NBA 2024-25 Overview</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h4 style='text-align: center; color: gray;'>A Global Look at the League</h4>",
    unsafe_allow_html=True
)

# ... rest of your home.py code ...