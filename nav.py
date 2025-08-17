# nav.py
import streamlit as st
from streamlit_option_menu import option_menu

def navbar():
    selected = option_menu(
        menu_title=None,  # No title for cleaner look
        options=["🏠 Home", "🏀 Team", "📊 Statistics", "🏆 Historic"],
        icons=["house", "people", "bar-chart", "trophy"],  # icons from Bootstrap
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#111"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#333",
            },
            "nav-link-selected": {"background-color": "#17408B"},
        },
    )
    return selected
