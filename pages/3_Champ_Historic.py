# -*- coding: utf-8 -*-
import unicodedata
import pandas as pd
import streamlit as st
import plotly.express as px

# --------------------------------------------------
# Run with:  streamlit run 3_Champ_Historic.py
# --------------------------------------------------
st.set_page_config(page_title="NBA History", layout="wide")

# -------------------------------
# Navigation bar (top of page)
# -------------------------------

from nav_bar import show_navbar  # 👈 import de la fonction

import plotly.express as px

# -------------------------------
# Navigation bar
# -------------------------------
show_navbar() 


# -------------------------------
# Load data
# -------------------------------
@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]
    df["RUNNER"] = df["RUNNER-UP"]  # unify runner-up column
    return df

df_raw = load_data("data/df_nba_champion.xlsx")

st.markdown(
    """
    <h1 style='text-align:center;margin-top:0'>NBA History — since 1976</h1>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# Helpers
# -------------------------------
def normalize_txt(s: str) -> str:
    """Lowercase + trim + remove accents. Handles None/NaN."""
    if s is None:
        return ""
    s = str(s)
    if s.lower() == "nan":
        return ""
    s = s.strip().casefold()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s



def bar_chart(data: pd.DataFrame, col_value: str, col_label: str, title: str, col_color: str | None = None):
    """Horizontal bar chart with values inside bars, clean layout."""
    data_sorted = data.sort_values(by=col_value, ascending=False)

    kwargs = dict(
        data_frame=data_sorted,
        x=col_value,
        y=col_label,
        orientation="h",
        title=title,
        text=col_value,
        category_orders={col_label: data_sorted[col_label].tolist()},
    )
    if col_color:
        kwargs["color"] = col_color

    fig = px.bar(**kwargs)

    fig.update_traces(
        texttemplate="%{text}",
        textposition="inside",
        insidetextanchor="start",
        textfont=dict(color="white", size=14, family="Arial"),
        marker_line_width=0,
    )

    fig.update_layout(
        xaxis=dict(visible=False),  # hide X axis
        yaxis=dict(showgrid=False, zeroline=False, title=None),  # 👈 hide Y axis label
        bargap=0.15,
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=120, r=60, t=60, b=40),
        title=dict(x=0.02, xanchor="left"),
    )
    return fig

# -------------------------------
# Prepare normalized columns
# -------------------------------
df = df_raw.copy()
for col in ["CHAMPION", "RUNNER", "FINALS_MVP", "POINTS", "REBOUNDS", "ASSISTS"]:
    df[f"{col}_NORM"] = df[col].map(normalize_txt)

df["PLAYERS_ALL_NORM"] = (
    df["FINALS_MVP_NORM"].fillna("") + "|" +
    df["POINTS_NORM"].fillna("") + "|" +
    df["REBOUNDS_NORM"].fillna("") + "|" +
    df["ASSISTS_NORM"].fillna("")
)

# -------------------------------
# Tabs
# -------------------------------
tab_history, tab_stats = st.tabs([" Champions Table", " Franchise Records"])

# ===== Tab 1: History of champions =====
# ===== Tab 1: History of champions =====
with tab_history:
    st.markdown("### Filter the history")

    years = ["All"] + sorted([y for y in df["YEAR"].dropna().unique().tolist()], reverse=True)
    champs = ["All"] + sorted([c for c in df["CHAMPION"].dropna().unique().tolist()])
    runners = ["All"] + sorted([r for r in df["RUNNER"].dropna().unique().tolist()])
    players = ["All"] + sorted(
        pd.concat([
            df["FINALS_MVP"].dropna(),
            df["POINTS"].dropna(),
            df["REBOUNDS"].dropna(),
            df["ASSISTS"].dropna(),
        ]).astype(str).unique().tolist()
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        year_filter = st.selectbox("Select Year", years, key="year_hist")
    with col2:
        champ_filter = st.selectbox("Select Champion", champs, key="champ_hist")
    with col3:
        runner_filter = st.selectbox("Select Runner-Up", runners, key="runner_hist")
    with col4:
        player_filter = st.selectbox("Select Player", players, key="player_hist")

    # Apply filters
    filtered = df.copy()

    def apply_eq(_df: pd.DataFrame, col: str, val):
        return _df if val == "All" else _df[_df[col] == val]

    filtered = apply_eq(filtered, "YEAR", year_filter)
    filtered = apply_eq(filtered, "CHAMPION", champ_filter)
    filtered = apply_eq(filtered, "RUNNER", runner_filter)

    if player_filter != "All":
        player_norm = normalize_txt(player_filter)
        filtered = filtered[filtered["PLAYERS_ALL_NORM"].str.split("|").apply(lambda lst: player_norm in lst)]

    st.markdown("### Results")

    if filtered.empty:
        st.info("No results for this filter combination.")
    else:
        # Subset 1: Finals summary
        df1 = filtered[["YEAR", "CHAMPION", "RUNNER-UP", "FINALS_MVP"]].dropna(how="all", axis=0)
        st.markdown("#### Finals Summary")
        st.dataframe(df1, hide_index=True, use_container_width=True)

        # Subset 2: Top playoff performers
        cols_perf = [c for c in ["POINTS", "REBOUNDS", "ASSISTS", "WIN_SHARES"] if c in filtered.columns]
        if cols_perf:
            df2 = filtered[["YEAR"] + cols_perf].dropna(how="all", axis=0)
            st.markdown("#### Top Playoff Performers")
            st.dataframe(df2, hide_index=True, use_container_width=True)

# ===== Tab 2: Franchise statistics =====
with tab_stats:
    st.markdown("### Franchise overview (since 1976)")

    df_all = df.copy()

    # 1) Most titles
    titles_count = (
        df_all.groupby("CHAMPION").size()
        .reset_index(name="Titles")
        .sort_values(by="Titles", ascending=False)
        .head(10)
    )

    # 2) Most Finals MVPs
    mvp_count = (
        df_all[df_all["FINALS_MVP"].notna()]
        .groupby("FINALS_MVP").size()
        .reset_index(name="Finals MVP Awards")
        .sort_values(by="Finals MVP Awards", ascending=False)
        .head(10)
    )

    # 3) Most Finals appearances
    team_appearances = (
        pd.concat([
            df_all[["CHAMPION"]].rename(columns={"CHAMPION": "Team"}),
            df_all[["RUNNER"]].rename(columns={"RUNNER": "Team"}),
        ])
        .dropna()
        .groupby("Team").size()
        .reset_index(name="Appearances")
        .sort_values(by="Appearances", ascending=False)
        .head(10)
    )

    # Display charts
    left, mid, right = st.columns(3)

    with left:
        fig1 = bar_chart(titles_count, col_value="Titles", col_label="CHAMPION", title="Most Titles by Team")
        st.plotly_chart(fig1, use_container_width=True, theme="streamlit")

    with mid:
        fig2 = bar_chart(mvp_count, col_value="Finals MVP Awards", col_label="FINALS_MVP", title="Most Finals MVPs")
        st.plotly_chart(fig2, use_container_width=True, theme="streamlit")

    with right:
        fig3 = bar_chart(team_appearances, col_value="Appearances", col_label="Team", title="Most Finals Appearances")
        st.plotly_chart(fig3, use_container_width=True, theme="streamlit")
