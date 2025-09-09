import pandas as pd
import streamlit as st
import plotly.express as px

# Lancer avec : py -m streamlit run test.py
st.set_page_config(layout="wide")

# -------------------------------
# Barre de navigation
# -------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.page_link("home.py",                   label=" Accueil")
with c2: st.page_link("pages/1_Team.py",           label=" Équipe")
with c3: st.page_link("pages/2_Statistics.py",     label=" Statistiques")
with c4: st.page_link("pages/3_Champ_Historic.py", label=" Historique")
with c5: st.page_link("pages/4_Trade_Machine.py",  label=" Simulateur de Trade")

# -------------------------------
# Données
# -------------------------------
df_nba_champion = pd.read_excel("data/df_nba_champion.xlsx")

st.markdown(
    "<h1 style='text-align: center;'>Historique NBA — depuis 1976</h1>",
    unsafe_allow_html=True
)

# -------------------------------
# Utilitaire : graphique en barres
# -------------------------------
def graphique_barres(data, col_valeur, col_label, titre, col_couleur=None):
    # Trier décroissant pour afficher les plus grands en haut
    data_sorted = data.sort_values(by=col_valeur, ascending=False)

    fig = px.bar(
        data_sorted,
        x=col_valeur,
        y=col_label,
        orientation="h",
        title=titre,
        text=col_valeur,
        color=col_couleur if col_couleur else None,
        category_orders={col_label: data_sorted[col_label].tolist()}
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
        bargap=0.001,
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=100, r=50, t=50, b=50)
    )

    return fig


# -------------------------------
# Onglets
# -------------------------------
onglet_hist, onglet_stats = st.tabs([" Tableau d’honneur", " Bilan des franchises"])

# ===== Onglet 1 : Historique des champions =====
with onglet_hist:
    st.markdown("### Filtrer le palmarès")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        year_filter = st.selectbox(
            "Sélectionner une année",
            ["Toutes"] + sorted(df_nba_champion["YEAR"].unique().tolist(), reverse=True),
            key="year_hist"
        )

    with col2:
        champ_filter = st.selectbox(
            "Sélectionner une équipe championne",
            ["Toutes"] + sorted(df_nba_champion["CHAMPION"].dropna().unique().tolist()),
            key="champ_hist"
        )

    with col3:
        runner_filter = st.selectbox(
            "Sélectionner une équipe finaliste",
            ["Toutes"] + sorted(df_nba_champion["RUNNER-UP"].dropna().unique().tolist()),
            key="runner_hist"
        )

    with col4:
        player_filter = st.selectbox(
            "Sélectionner un joueur",
            ["Toutes"] + sorted(
                pd.concat([
                    df_nba_champion["FINALS_MVP"].dropna(),
                    df_nba_champion["POINTS"].dropna(),
                    df_nba_champion["REBOUNDS"].dropna(),
                    df_nba_champion["ASSISTS"].dropna()
                ]).unique().tolist()
            ),
            key="player_hist"
        )

    # Application des filtres
    filtered_df = df_nba_champion.copy()

    if year_filter != "Toutes":
        filtered_df = filtered_df[filtered_df["YEAR"] == year_filter]

    if champ_filter != "Toutes":
        filtered_df = filtered_df[filtered_df["CHAMPION"] == champ_filter]

    if runner_filter != "Toutes":
        # Si ton dataset utilise "TM_RUNNER_UP", garde cette ligne ; sinon remplace par "RUNNER-UP"
        filtered_df = filtered_df[filtered_df["TM_RUNNER_UP"] == runner_filter]

    if player_filter != "Toutes":
        mask = (
            filtered_df["FINALS_MVP"].str.contains(player_filter, na=False) |
            filtered_df["POINTS"].str.contains(player_filter, na=False) |
            filtered_df["REBOUNDS"].str.contains(player_filter, na=False) |
            filtered_df["ASSISTS"].str.contains(player_filter, na=False)
        )
        filtered_df = filtered_df[mask]

    st.markdown("### Résultats")
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)


    
# ===== Onglet 2 : Statistiques globales d’équipe =====
with onglet_stats:
    st.markdown("### Vue d’ensemble — franchises")

    # 1) Plus de titres par équipe (Top 10)
    titles_count = (
        df_nba_champion.groupby("CHAMPION")
        .size()
        .reset_index(name="Titres")
        .sort_values(by="Titres", ascending=False)
        .head(10)
    )
    st.markdown("####  Top 10 équipes par nombre de titres")
    st.dataframe(titles_count, hide_index=True, use_container_width=True)

    # 2) Plus de trophées Finals MVP par joueur (Top 10)
    mvp_count = (
        df_nba_champion.groupby("FINALS_MVP")
        .size()
        .reset_index(name="Trophées MVP")
        .sort_values(by="Trophées MVP", ascending=False)
        .head(10)
    )
    st.markdown("####  Top 10 joueurs avec le plus de Finals MVP")
    st.dataframe(mvp_count, hide_index=True, use_container_width=True)

    # 3) Plus de participations en finales par équipe (Top 10)
    team_appearances = (
        pd.concat([
            df_nba_champion[["CHAMPION"]].rename(columns={"CHAMPION": "Équipe"}),
            df_nba_champion[["RUNNER-UP"]].rename(columns={"RUNNER-UP": "Équipe"})
        ])
        .groupby("Équipe")
        .size()
        .reset_index(name="Participations")
        .sort_values(by="Participations", ascending=False)
        .head(10)
    )
    st.markdown("####  Top 10 équipes par participations en finales")
    st.dataframe(team_appearances, hide_index=True, use_container_width=True)
