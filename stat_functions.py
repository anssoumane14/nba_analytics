import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------------------
# Utilitaire : graphique en barres
# -------------------------------
def graphique_barres(data, col_name, titre):
    data_sorted = data.sort_values(by=col_name, ascending=False)
    fig = px.bar(
        data_sorted,
        x=col_name,
        y="PLAYER",
        orientation="h",
        color="TEAM",
        title=titre,
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
# Fonctions d'affichage
# -------------------------------
def afficher_offensif(df, label, mode, view_mode):
    suffix = "_PG" if mode == "Par match" else ""
    st.markdown(f"##  Statistiques offensives ({label} - {mode})")

    stats = {
        "Points": "PTS",
        "Passes décisives": "AST",
        "3 points marqués": "3P",
        "Lancers francs marqués": "FT"
    }

    col1, col2 = st.columns(2)
    for (titre, col_name), col in zip(stats.items(), [col1, col2, col1, col2]):
        top_data = (
            df[["PLAYER", "TEAM", col_name + suffix]]
            .sort_values(by=col_name + suffix, ascending=False)
            .head(5)
        )
        if view_mode == "Tableau":
            col.markdown(f"### {titre} {mode}")
            col.dataframe(top_data, hide_index=True, use_container_width=True)
        else:
            fig = graphique_barres(top_data, col_name + suffix, f"{titre}")
            col.plotly_chart(fig, use_container_width=True)

def afficher_defensif(df, label, mode, view_mode):
    suffix = "_PG" if mode == "Par match" else ""
    st.markdown(f"##  Statistiques défensives ({label} - {mode})")

    stats = {
        "Rebonds totaux": "TRB",
        "Rebonds défensifs": "DRB",
        "Contres": "BLK",
        "Interceptions": "STL"
    }

    col1, col2 = st.columns(2)
    for (titre, col_name), col in zip(stats.items(), [col1, col2, col1, col2]):
        top_data = (
            df[["PLAYER", "TEAM", col_name + suffix]]
            .sort_values(by=col_name + suffix, ascending=False)
            .head(5)
        )
        if view_mode == "Tableau":
            col.markdown(f"### {titre} {mode}")
            col.dataframe(top_data, hide_index=True, use_container_width=True)
        else:
            fig = graphique_barres(top_data, col_name + suffix, f"{titre}")
            col.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Fonction pour choisir les colonnes
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

    options = ["Tout sélectionner"] + extras
    selected_extra = st.multiselect(
        "Ajouter des colonnes à afficher",
        options=options,
        default=[],
        key=key
    )
    if "Tout sélectionner" in selected_extra:
        selected_extra = extras
    return defaults + selected_extra
