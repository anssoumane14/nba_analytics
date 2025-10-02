# nav_bar.py
import streamlit as st

def show_navbar():
    # -------------------------------
    # Simple navigation bar
    # -------------------------------
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.page_link("home.py", label="Home")
    with c2:
        st.page_link("pages/1_Team.py", label="Teams")
    with c3:
        st.page_link("pages/2_Statistics.py", label="Statistics")
    with c4:
        st.page_link("pages/3_Champ_Historic.py", label="History")
