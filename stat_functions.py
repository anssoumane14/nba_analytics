import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------------------
# Bar chart (horizontal)
# -------------------------------
def graphique_barres(data, col_name, title):
    data_sorted = data.sort_values(by=col_name, ascending=False)
    fig = px.bar(
        data_sorted,
        x=col_name,
        y="PLAYER",
        orientation="h",
        color="TEAM",
        title=title,
        text=col_name,
        category_orders={"PLAYER": data_sorted["PLAYER"].tolist()}
    )
    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        insidetextanchor="end",
        textfont=dict(color="grey", size=14, family="Arial")
    )
    fig.update_layout(
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        bargap=0.2,
        plot_bgcolor="white",
        showlegend=True
    )
    return fig


# -------------------------------
# Bar chart (vertical)
# -------------------------------
def graphique_barres_v2(data, col_name, title):
    data_sorted = data.sort_values(by=col_name, ascending=False)
    fig = px.bar(
        data_sorted,
        x="PLAYER",
        y=col_name,
        color="TEAM",
        title=title,
        text=col_name
    )
    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        insidetextanchor="end",
        textfont=dict(color="grey", size=12, family="Arial")
    )
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, tickangle=-45),
        yaxis=dict(showgrid=False, zeroline=False, title=None),
        bargap=0.2,
        plot_bgcolor="white",
        showlegend=True,
        height=600,
        margin=dict(t=50, b=100)
    )
    return fig


# -------------------------------
# Offensive Stats (leaders)
# -------------------------------
def afficher_offensif_v2(df, label, mode, view_mode):
    suffix = "_PG" if mode == "Per Game" else ""
    st.markdown(f"## Offensive Statistics ({label} - {mode})")

    stats = {
        "Points": "PTS",
        "Assists": "AST",
        "3-Pointers Made": "3P",
        "Free Throws Made": "FT"
    }

    col1, col2 = st.columns(2)
    for (title, col_name), col in zip(stats.items(), [col1, col2, col1, col2]):
        top_data = (
            df[["PLAYER", "TEAM", col_name + suffix]]
            .sort_values(by=col_name + suffix, ascending=False)
            .head(5)
        )
        if view_mode == "Tableau":
            col.markdown(f"### {title} {mode}")
            col.dataframe(top_data, hide_index=True, use_container_width=True)
        else:
            fig = graphique_barres_v2(top_data, col_name + suffix, f"{title}")
            col.plotly_chart(fig, use_container_width=True)


# -------------------------------
# Defensive Stats (leaders)
# -------------------------------
def afficher_defensif_v2(df, label, mode, view_mode):
    suffix = "_PG" if mode == "Per Game" else ""
    st.markdown(f"## Defensive Statistics ({label} - {mode})")

    stats = {
        "Total Rebounds": "TRB",
        "Defensive Rebounds": "DRB",
        "Blocks": "BLK",
        "Steals": "STL"
    }

    col1, col2 = st.columns(2)
    for (title, col_name), col in zip(stats.items(), [col1, col2, col1, col2]):
        top_data = (
            df[["PLAYER", "TEAM", col_name + suffix]]
            .sort_values(by=col_name + suffix, ascending=False)
            .head(5)
        )
        if view_mode == "Tableau":
            col.markdown(f"### {title} {mode}")
            col.dataframe(top_data, hide_index=True, use_container_width=True)
        else:
            fig = graphique_barres_v2(top_data, col_name + suffix, f"{title}")
            col.plotly_chart(fig, use_container_width=True)


# -------------------------------
# Column picker (for All Data)
# -------------------------------
def pick_display_columns(
    df: pd.DataFrame,
    base_cols=("TEAM", "PLAYER", "PTS_PG", "AST_PG", "TRB_PG", "MP_PG"),
    exclude=("PLAYER_ID", "RK"),
    key="col_picker"
) -> list:
    exclude = set(exclude)
    available = [c for c in df.columns if c not in exclude]
    defaults = [c for c in base_cols if c in available]
    extras = [c for c in available if c not in defaults]

    options = ["Select All"] + extras
    selected_extra = st.multiselect(
        "Add columns to display",
        options=options,
        default=[],
        key=key
    )
    if "Select All" in selected_extra:
        selected_extra = extras
    return defaults + selected_extra


# -------------------------------
# Compare RS vs PO
# -------------------------------
def compare_rs_vs_po(df_rs, df_po, player: str, season: str):
    rs_row = df_rs[(df_rs["PLAYER"] == player) & (df_rs["SEASON"] == season)]
    po_row = df_po[(df_po["PLAYER"] == player) & (df_po["SEASON"] == season)]

    if rs_row.empty or po_row.empty:
        st.warning("Not enough data for this comparison.")
        return

    rs_row, po_row = rs_row.iloc[0], po_row.iloc[0]

    base_metrics = {
        "Points": "PTS_PG",
        "Assists": "AST_PG",
        "Rebounds": "TRB_PG",
        "Steals": "STL_PG",
        "Blocks": "BLK_PG",
        "Minutes": "MP_PG",
    }

    data = []
    for label, col in base_metrics.items():
        if col in rs_row and col in po_row:
            data.append([label, rs_row[col], po_row[col]])

    df_diff = pd.DataFrame(data, columns=["Stat", "Regular Season", "Playoffs"])
    df_melt = df_diff.melt(id_vars="Stat", value_vars=["Regular Season", "Playoffs"], 
                           var_name="Context", value_name="Value")

    fig = px.bar(df_melt, x="Stat", y="Value", color="Context", barmode="group", text="Value")
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=500,
        plot_bgcolor="white",
        margin=dict(t=40, b=40, l=20, r=20),
        yaxis=dict(showgrid=False, visible=False),
        xaxis=dict(title=None, showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)


# -------------------------------
# Compare two seasons
# -------------------------------
def compare_seasons(df, player: str, season1: str, season2: str, context_label="Regular Season"):
    row1 = df[(df["PLAYER"] == player) & (df["SEASON"] == season1)]
    row2 = df[(df["PLAYER"] == player) & (df["SEASON"] == season2)]

    if row1.empty or row2.empty:
        st.warning("Not enough data for this comparison.")
        return

    row1, row2 = row1.iloc[0], row2.iloc[0]

    base_metrics = {
        "Points": "PTS_PG",
        "Assists": "AST_PG",
        "Rebounds": "TRB_PG",
        "Steals": "STL_PG",
        "Blocks": "BLK_PG",
        "Minutes": "MP_PG",
    }

    data = []
    for label, col in base_metrics.items():
        if col in row1 and col in row2:
            data.append([label, row1[col], row2[col]])

    df_diff = pd.DataFrame(data, columns=["Stat", season1, season2])
    df_melt = df_diff.melt(id_vars="Stat", value_vars=[season1, season2],
                           var_name="Season", value_name="Value")

    fig = px.bar(df_melt, x="Stat", y="Value", color="Season", barmode="group", text="Value")
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=500,
        plot_bgcolor="white",
        margin=dict(t=40, b=40, l=20, r=20),
        yaxis=dict(showgrid=False, visible=False),
        xaxis=dict(title=None, showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)


# -------------------------------
# KPI Utilities
# -------------------------------

def render_kpi(df: pd.DataFrame, value_col: str, title: str):
    """Affiche une carte KPI simple pour la valeur max d'une colonne donnée."""
    if df.empty or value_col not in df.columns or df[value_col].dropna().empty:
        st.info(f"No data for {title}.")
        return

    idx = df[value_col].idxmax()
    row = df.loc[idx]
    val = float(row[value_col])
    player_name = str(row.get("PLAYER", "Unknown"))

    width_px = 280
    st.markdown(
        f"""
        <div style="background:#17408B; color:#FFFFFF; padding:16px; border-radius:12px; width:{width_px}px;">
            <div style="font-size:14px; opacity:.85; margin-bottom:6px; text-align:center;">{title}</div>
            <div style="font-size:32px; font-weight:700; line-height:1; text-align:center;">{val:.1f}</div>
            <div style="font-size:13px; opacity:.9; margin-top:6px; text-align:center;">{player_name}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
def render_kpi(df: pd.DataFrame, value_col: str, title: str):
    """Affiche une carte KPI simple pour la valeur max d'une colonne donnée."""
    if df.empty or value_col not in df.columns or df[value_col].dropna().empty:
        st.info(f"No data for {title}.")
        return

    idx = df[value_col].idxmax()
    row = df.loc[idx]
    val = float(row[value_col])
    player_name = str(row.get("PLAYER", "Unknown"))

    width_px = 220
    st.markdown(
        f"""
        <div style="background:#17408B; color:#FFFFFF; padding:16px; border-radius:12px; width:{width_px}px;">
            <div style="font-size:14px; opacity:.85; margin-bottom:6px; text-align:center;">{title}</div>
            <div style="font-size:32px; font-weight:700; line-height:1; text-align:center;">{val:.1f}</div>
            <div style="font-size:13px; opacity:.9; margin-top:6px; text-align:center;">{player_name}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_kpi_box(title: str, value_text: str, subtitle: str = "") -> str:
    """Return the HTML of a KPI card with proper spacing."""
    width_px = 220
    return f"""
        <div style="
            background:#17408B;
            color:#FFFFFF;
            padding:16px;
            border-radius:12px;
            width:{width_px}px;
            margin:auto;
            margin-bottom:20px;
        ">
            <div style="font-size:14px; opacity:.85; margin-bottom:6px; text-align:center;">{title}</div>
            <div style="font-size:32px; font-weight:700; line-height:1; text-align:center;">{value_text}</div>
            <div style="font-size:13px; opacity:.9; margin-top:6px; text-align:center;">{subtitle}</div>
        </div>
    """


def compute_player_career_stats(df: pd.DataFrame, player: str, season_type: str) -> dict:
    """Compute career averages (weighted) and totals for a player."""
    if df.empty:
        return {}

    player_df = df[df["PLAYER"] == player]
    if player_df.empty:
        return {}

    total_games = player_df["G"].sum() if "G" in player_df.columns else 0

    def weighted_avg(col_pg, col_total):
        if col_pg in player_df.columns and col_total in player_df.columns and total_games > 0:
            return player_df[col_total].sum() / total_games
        return None

    stats = {}
    # ✅ Career averages
    stats["PPG"] = weighted_avg("PTS_PG", "PTS")
    stats["RPG"] = weighted_avg("TRB_PG", "TRB")
    stats["APG"] = weighted_avg("AST_PG", "AST")
    stats["STL"] = weighted_avg("STL_PG", "STL")
    stats["BLK"] = weighted_avg("BLK_PG", "BLK")
    stats["TOV"] = weighted_avg("TOV_PG", "TOV")

    # ✅ Career totals
    stats["PTS_total"] = player_df["PTS"].sum() if "PTS" in player_df.columns else None
    stats["AST_total"] = player_df["AST"].sum() if "AST" in player_df.columns else None
    stats["TRB_total"] = player_df["TRB"].sum() if "TRB" in player_df.columns else None
    stats["STL_total"] = player_df["STL"].sum() if "STL" in player_df.columns else None
    stats["BLK_total"] = player_df["BLK"].sum() if "BLK" in player_df.columns else None
    stats["TOV_total"] = player_df["TOV"].sum() if "TOV" in player_df.columns else None
    stats["G_total"] = total_games

    # ✅ Triple-doubles
    if season_type == "Regular Season" and "TRP-DBL" in player_df.columns:
        stats["Triple Doubles"] = player_df["TRP-DBL"].sum()

    return stats


def display_kpi_cards(df: pd.DataFrame, player: str, season_type: str):
    """Display KPI cards in 2 rows (career averages only)."""
    stats = compute_player_career_stats(df, player, season_type)
    if stats is None or len(stats) == 0:
        st.info("⚠️ No data available.")
        return

    st.markdown("### 📊 Career Averages")

    labels = {
        "PPG": "Points Per Game",
        "RPG": "Rebounds Per Game",
        "APG": "Assists Per Game",
        "STL": "Steals Per Game",
        "BLK": "Blocks Per Game",
        "TOV": "Turnovers Per Game",
        "Triple Doubles": "Triple Doubles (Regular Season)"
    }

    # --- Ligne 1 : PPG, RPG, APG, Triple Doubles (si RS)
    keys_row1 = ["PPG", "RPG", "APG"]
    if season_type == "Regular Season" and "Triple Doubles" in stats:
        keys_row1.append("Triple Doubles")

    cols1 = st.columns(len(keys_row1))
    for i, key in enumerate(keys_row1):
        if key in stats and stats[key] is not None:
            value = f"{stats[key]:.1f}" if key != "Triple Doubles" else f"{int(stats[key])}"
            cols1[i].markdown(render_kpi_box(labels[key], value), unsafe_allow_html=True)

    # --- Espace entre les lignes
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # --- Ligne 2 : STL, BLK, TOV
    keys_row2 = ["STL", "BLK", "TOV"]
    cols2 = st.columns(len(keys_row2))
    for i, key in enumerate(keys_row2):
        if key in stats and stats[key] is not None:
            value = f"{stats[key]:.1f}"
            cols2[i].markdown(render_kpi_box(labels[key], value), unsafe_allow_html=True)



import streamlit as st

# -------------------------------
# HTML Render Helpers
# -------------------------------
def render_award_card(title: str, player: str, stats_text: str = "") -> str:
    """Large KPI card for MVP, ROY etc."""
    return f"""
        <div style="
            background:#17408B;
            color:#FFFFFF;
            padding:20px;
            border-radius:15px;
            width:350px;
            height:180px;
            margin:auto;
            margin-bottom:20px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            text-align:center;
        ">
            <div style="font-size:16px; opacity:.85; margin-bottom:10px;">{title}</div>
            <div style="font-size:26px; font-weight:700; line-height:1.2; word-wrap:break-word;">{player}</div>
            <div style="font-size:14px; opacity:.9; margin-top:8px;">{stats_text}</div>
        </div>
    """

def render_stat_leader(title: str, value: str, subtitle: str = "") -> str:
    """Compact KPI card for leaders (PPG, RPG, APG, WS)."""
    return f"""
        <div style="
            background:#17408B;
            color:#FFFFFF;
            padding:16px;
            border-radius:12px;
            width:220px;
            height:120px;
            margin:auto;
            margin-bottom:20px;
            text-align:center;
        ">
            <div style="font-size:14px; opacity:.85; margin-bottom:6px;">{title}</div>
            <div style="font-size:28px; font-weight:700; line-height:1;">{value}</div>
            <div style="font-size:13px; opacity:.9; margin-top:6px;">{subtitle}</div>
        </div>
    """

# -------------------------------
# Display Awards KPI
# -------------------------------
def display_awards_kpi(df_awards, season: str):
    if df_awards.empty:
        st.info("⚠️ No awards data available.")
        return

    df_season = df_awards[df_awards["SEASON"] == season]
    if df_season.empty:
        st.info(f"⚠️ No awards found for season {season}.")
        return

    # --- Line 1 : MVP + ROY
    col1, col2 = st.columns(2)
    mvp = df_season[df_season["AWARD"] == "Most Valuable Player"]
    roy = df_season[df_season["AWARD"] == "Rookie of the Year"]

    if not mvp.empty:
        row = mvp.iloc[0]
        stats_text = f"{row['PPG']} PPG | {row['RPG']} RPG | {row['APG']} APG"
        col1.markdown(render_award_card("Most Valuable Player", row["NAME"], stats_text), unsafe_allow_html=True)

    if not roy.empty:
        row = roy.iloc[0]
        stats_text = f"{row['PPG']} PPG | {row['RPG']} RPG | {row['APG']} APG"
        col2.markdown(render_award_card("Rookie of the Year", row["NAME"], stats_text), unsafe_allow_html=True)

    # --- Space
    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

    # --- Line 2 : Leaders (PPG, RPG, APG, WS)
    leaders = {
        "PPG Leader": "PPG",
        "RPG Leader": "RPG",
        "APG Leader": "APG",
        "WS Leader": "WS",
    }

    cols = st.columns(len(leaders))
    i = 0
    for award_name, stat_col in leaders.items():
        row = df_season[df_season["AWARD"] == award_name]
        if not row.empty:
            row = row.iloc[0]
            value = row[stat_col] if pd.notna(row[stat_col]) else ""
            player = row["NAME"] if pd.notna(row["NAME"]) else ""
            cols[i].markdown(render_stat_leader(award_name, f"{value}", player), unsafe_allow_html=True)
        i += 1
