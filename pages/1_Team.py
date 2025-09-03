# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from nav import navbar # Importation potentielle de la barre de navigation

# -------------------------------
# Configuration de la Page
# -------------------------------
st.set_page_config(page_title="Équipe", layout="wide") # Configure le titre de la page et la disposition large

# -------------------------------
# Affichage de la Barre de Navigation
# -------------------------------
# Note : La barre de navigation est actuellement implémentée directement via st.page_link.
# Pour une implémentation modulable, l'utilisation de la fonction navbar() importée serait envisagée.
c1, c2, c3, c4,c5 = st.columns(5) # Crée 5 colonnes pour les liens de navigation
with c1: st.page_link("home.py",                   label="🏠 Accueil")
with c2: st.page_link("pages/1_Team.py",           label="🏀 Équipe")
with c3: st.page_link("pages/2_Statistics.py",     label="📊 Statistiques")
with c4: st.page_link("pages/3_Champ_Historic.py", label="🏆 Historique")
with c5: st.page_link("pages/4_Trade_Machine.py",  label="💸 Machine à Trade")


# -------------------------------
# Chargement des Données
# -------------------------------
df_west = pd.read_excel("data/df_western_conf_standing.xlsx") # Charge les classements de la Conférence Ouest
df_east = pd.read_excel("data/df_eastern_conf_standing.xlsx") # Charge les classements de la Conférence Est
df_team_ratings = pd.read_excel("data/df_nba_team_reg_season_ratings.xlsx") # Charge les évaluations des équipes de saison régulière
df_reg_players = pd.read_excel("data/df_reg_season_players_filtered.xlsx") # Charge les données filtrées des joueurs de saison régulière
df_po_players = pd.read_excel("data/df_playoff_players_filtered.xlsx") # Charge les données filtrées des joueurs de playoffs
df_salaries = pd.read_excel("data/df_nba_players_salaries.xlsx") # Charge les salaires des joueurs

# -------------------------------
# Application de Filtres de Qualité des Joueurs
# -------------------------------
# Filtre les joueurs pour ne conserver que ceux ayant joué plus de 10 matchs et plus de 10 minutes par match.
# Ceci s'applique aux DataFrames de saison régulière et de playoffs.
df_reg_players = df_reg_players[(df_reg_players["GP"] > 10) & (df_reg_players["MIN_PG"] > 10)]
df_po_players = df_po_players[(df_po_players["GP"] > 10) & (df_po_players["MIN_PG"] > 10)]


# -------------------------------
# Fonctions d'Affichage KPI
# -------------------------------
def render_kpi(df, value_col, title):
    """
    Affiche une carte KPI pour le joueur ayant la valeur maximale dans une colonne donnée.
    """
    if df.empty or value_col not in df.columns or df[value_col].dropna().empty:
        st.info(f"Aucune donnée pour {title}.")
        return

    # Trouve l'index du joueur avec la valeur maximale
    idx = df[value_col].idxmax()
    row = df.loc[idx] # Récupère la ligne correspondante
    val = float(row[value_col]) # Valeur du KPI
    player_name = str(row.get("PLAYER_NAME", "Inconnu")) # Nom du joueur
    team_name = str(row.get("TEAM", row.get("TEAM_ABBREVIATION", ""))) # Nom de l'équipe

    width_px = 320
    # Utilise du Markdown avec du HTML unsafe pour styliser la carte KPI
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

def render_kpi_box(title, value_text, subtitle=""):
    """
    Affiche une carte KPI générique avec un titre, une valeur et un sous-titre.
    """
    width_px = 320
    # Utilise du Markdown avec du HTML unsafe pour styliser la carte KPI
    st.markdown(
        f"""
        <div style="background:#17408B; color:#FFFFFF; padding:16px; border-radius:12px; width:{width_px}px;">
            <div style="font-size:14px; opacity:.85; margin-bottom:6px; text-align:center;">{title}</div>
            <div style="font-size:32px; font-weight:700; line-height:1; text-align:center;">{value_text}</div>
            <div style="font-size:13px; opacity:.9; margin-top:6px; text-align:center;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------------
# Titre de la Page
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>🏀 Aperçu de l'Équipe NBA 2024-25</h1>",
    unsafe_allow_html=True
)

# -------------------------------
# Filtre Global par Équipe
# -------------------------------
team_options = sorted(df_reg_players["TEAM"].dropna().unique()) # Récupère la liste unique des équipes
selected_team = st.selectbox("Sélectionnez une Équipe", team_options, index=0, key="team_filter") # Sélecteur d'équipe

# -------------------------------
# Construction des Classements Combinés (avec drapeaux et rang)
# -------------------------------
df_west_local = df_west.copy() # Copie locale des classements Ouest
df_east_local = df_east.copy() # Copie locale des classements Est

df_west_local["CONF"] = "Ouest" # Ajoute la colonne Conférence
df_east_local["CONF"] = "Est" # Ajoute la colonne Conférence

# Si les classements sont déjà triés, le rang est l'ordre des lignes
df_west_local["RANK"] = range(1, len(df_west_local) + 1)
df_east_local["RANK"] = range(1, len(df_east_local) + 1)

df_standings = pd.concat([df_east_local, df_west_local], ignore_index=True) # Concatène les classements

def to_bool_playoff(x):
    """Convertit l'indicateur de playoff en booléen."""
    s = str(x).strip().lower()
    return s in ("*", "true", "1")

# Vérifie et convertit la colonne PLAYOFF_TEAM en booléen si nécessaire
if "PLAYOFF_TEAM" in df_standings.columns:
    if df_standings["PLAYOFF_TEAM"].dtype != bool:
        df_standings["PLAYOFF_TEAM"] = df_standings["PLAYOFF_TEAM"].apply(to_bool_playoff)
else:
    df_standings["PLAYOFF_TEAM"] = False # Par défaut si la colonne n'existe pas

# Recherche le rang de l'équipe sélectionnée
team_row = df_standings[df_standings["TEAM"] == selected_team]
if not team_row.empty:
    conf = team_row.iloc[0]["CONF"] # Conférence de l'équipe
    rank = int(team_row.iloc[0]["RANK"]) # Rang de l'équipe
    st.markdown(f"**Conférence :** {conf} — **Rang :** #{rank}") # Affiche la conférence et le rang
else:
    st.info("Équipe sélectionnée non trouvée dans les classements.") # Message si l'équipe n'est pas trouvée


# -------------------------------
# Sélection des Données Générales (Saison Régulière vs. Playoffs)
# -------------------------------
season_filter = st.radio(
        "Type de Saison",
        ["Saison Régulière", "Playoffs"],
        horizontal=True,
        key="season_filter_team"
    )

# Sélectionne le bon jeu de données en fonction du type de saison
df = df_reg_players if season_filter == "Saison Régulière" else df_po_players

# Applique le filtre global d'équipe
df = df[df["TEAM"] == selected_team]

# Si les playoffs sont sélectionnés mais que l'équipe n'y a pas participé, arrête l'affichage de cet onglet
if season_filter == "Playoffs":
    row = df_standings[df_standings["TEAM"] == selected_team]
    is_po = bool(row["PLAYOFF_TEAM"].iloc[0]) if not row.empty else False
    if not is_po:
        st.warning(f"{selected_team} n'a pas participé aux playoffs en 2024-25 — aucune statistique de joueur de playoffs à afficher.")
        st.stop() # Arrête l'exécution du script Streamlit pour cet onglet

st.markdown(f"### Statistiques de l'Équipe — {selected_team}")
st.markdown("## 📌 Statistiques Générales")

# -------------------------------
# Onglets (Marque-pages)
# -------------------------------
tab_stats, tab_salaries = st.tabs(["📊 Statistiques de l'Équipe", "💰 Salaires"])


# ===============================
# 📊 I. Statistiques de l'Équipe
# ===============================
with tab_stats:

    # --- Première ligne de KPIs ---
    c1, c2, c3 = st.columns(3) # Crée 3 colonnes pour les KPIs
    with c1:
        render_kpi(df, "PTS_PG", "Points par Match") # Affiche le KPI Points par Match
    with c2:
        render_kpi(df, "REB_PG", "Rebonds par Match") # Affiche le KPI Rebonds par Match
    with c3:
        render_kpi(df, "AST_PG", "Passes Décisives par Match") # Affiche le KPI Passes Décisives par Match

    st.markdown("<br>", unsafe_allow_html=True) # Ajoute un saut de ligne HTML pour l'espacement

    # --- Deuxième ligne de KPIs ---
    c4, c5, c6 = st.columns(3) # Crée 3 colonnes pour les KPIs
    with c4:
        render_kpi(df, "STL_PG", "Interceptions par Match") # Affiche le KPI Interceptions par Match
    with c5:
        render_kpi(df, "BLK_PG", "Contres par Match") # Affiche le KPI Contres par Match
    with c6:
        render_kpi(df, "TOV_PG", "Pertes de Balle par Match") # Affiche le KPI Pertes de Balle par Match

    st.markdown("<br>", unsafe_allow_html=True) # Espacement
    st.markdown("<br>", unsafe_allow_html=True) # Espacement
    st.markdown("<br>", unsafe_allow_html=True) # Espacement

    # --------------------------------
    # Effectif Complet de l'Équipe — Style de Paramètre de Champ
    # --------------------------------
    st.markdown("## Effectif Complet")

    # Colonnes par défaut (ne conserve que celles qui existent réellement dans le DataFrame)
    default_cols = [c for c in ["TEAM", "PLAYER_NAME", "PTS_PG", "AST_PG", "REB_PG", "MIN_PG"] if c in df.columns]

    # Champs additionnels que l'utilisateur peut ajouter en plus des colonnes par défaut
    additional_fields = [c for c in df.columns if c not in default_cols]

    # Sélecteur multiple avec une option "Tout sélectionner"
    multiselect_options = ["Tout sélectionner"] + additional_fields
    selected_extra = st.multiselect(
        "Ajouter des colonnes à afficher",
        options=multiselect_options,
        default=[],
        key="team_full_fields"
    )

    # Étend la sélection si "Tout sélectionner" est choisi
    if "Tout sélectionner" in selected_extra:
        selected_extra = additional_fields

    # Liste finale des colonnes à afficher
    cols_to_show = default_cols + selected_extra

    if cols_to_show:
        st.dataframe(df[cols_to_show], hide_index=True, use_container_width=True) # Affiche le DataFrame des joueurs
    else:
        st.info("Aucune colonne sélectionnée. Veuillez en choisir au moins une.") # Message si aucune colonne n'est choisie


# ===============================
# 💰 II. Salaires
# ===============================

# -------------------------------
# Dépivotement des Salaires
# -------------------------------
year_cols = ["2025-26", "2026-27", "2027-28", "2028-29", "2029-30", "2030-31", "GUARANTEED"]

# Transforme le DataFrame des salaires du format large au format long (dépivotement)
df_salaries_unpivoted = df_salaries.melt(
    id_vars=["PLAYER", "TEAM"], # Colonnes à conserver telles quelles
    value_vars=year_cols, # Colonnes à dépivoter
    var_name="YEAR", # Nouveau nom de colonne pour les années
    value_name="SALARY" # Nouveau nom de colonne pour les valeurs de salaire
)


# -------------------------------
# Jointure des Salaires avec les Joueurs pour Obtenir la Position
# -------------------------------
# Prépare un DataFrame allégé des joueurs avec les infos nécessaires pour la jointure
df_players_slim = df_reg_players[["PLAYER_NAME", "TEAM", "POSITION","PTS_PG","AST_PG","REB_PG"]]
df_players_slim = df_players_slim.rename(columns={"PLAYER_NAME": "PLAYER"}) # Renomme pour la jointure

# Fusionne les salaires (format long) avec les informations des joueurs pour obtenir la position et les stats clés
df_join = pd.merge(
    df_salaries_unpivoted,   # DataFrame des salaires (Joueur, Équipe, Année, Salaire)
    df_players_slim,         # DataFrame des joueurs (Joueur, Équipe, Position)
    how="left", # Jointure à gauche pour conserver tous les salaires et ajouter les infos joueur si match
    on=["PLAYER", "TEAM"] # Clés de jointure
)

# Ajoute une colonne de salaire numérique (supprime les caractères non-numériques et convertit en entier)
df_join["SALARY_NUM"] = (
    df_join["SALARY"]
    .astype(str) # Convertit en chaîne pour la manipulation
    .str.replace(r"[^0-9]", "", regex=True) # Supprime tous les caractères non numériques
    .replace("", "0") # Remplace les chaînes vides par "0" pour la conversion en entier
    .astype(int) # Convertit en entier
)

# ===============================
# 💰 Salaires (camembert par position)
# ===============================
with tab_salaries:
    st.markdown(f"### Salaires des Joueurs — {selected_team}")

    # Récupère toutes les années de salaire disponibles (hors "GUARANTEED")
    all_years = sorted([y for y in df_salaries_unpivoted["YEAR"].dropna().unique() if str(y) != "GUARANTEED"])
    selected_year = st.selectbox("Sélectionnez la Saison", all_years, index=0) # Sélecteur d'année

    # Filtre le DataFrame des salaires joints pour l'équipe et l'année sélectionnées
    df_team_year = df_join[(df_join["TEAM"] == selected_team) & (df_join["YEAR"] == selected_year)].copy()


    # ===============================
    # Cartes KPI pour l'année sélectionnée
    # ===============================

    # --- 1) Calcule les valeurs des KPIs à partir de df_team_year (déjà filtré par ÉQUIPE + ANNÉE)
    team_total = int(df_team_year["SALARY_NUM"].sum()) # Calcul du payroll total de l'équipe

    if not df_team_year.empty and df_team_year["SALARY_NUM"].max() > 0:
        top_row = df_team_year.loc[df_team_year["SALARY_NUM"].idxmax()] # Ligne du joueur le mieux payé
        top_player = str(top_row["PLAYER"]) # Nom du joueur le mieux payé
        top_salary = int(top_row["SALARY_NUM"]) # Salaire du joueur le mieux payé
    else:
        top_player, top_salary = "—", 0 # Valeurs par défaut si pas de données

    # "Valeur" : (Points+Passes+Rebonds par match) par million de dollars pour cette équipe et cette année
    df_val = df_team_year.copy()
    df_val[["PTS_PG","AST_PG","REB_PG"]] = df_val[["PTS_PG","AST_PG","REB_PG"]].fillna(0) # Gère les NaN
    df_val["salary_m"] = df_val["SALARY_NUM"].replace(0, pd.NA) / 1_000_000 # Salaire en millions de dollars
    df_val["value_score"] = (df_val["PTS_PG"] + df_val["AST_PG"] + df_val["REB_PG"]) / df_val["salary_m"] # Calcul du score de valeur

    if df_val["value_score"].dropna().empty:
        best_value_player, best_value_score = "—", 0.0 # Valeurs par défaut si pas de données
    else:
        best_row = df_val.loc[df_val["value_score"].idxmax()] # Ligne du joueur avec le meilleur score de valeur
        best_value_player = str(best_row["PLAYER"]) # Nom du joueur avec le meilleur score de valeur
        best_value_score  = float(best_row["value_score"]) # Score de valeur

    # --- ) Affiche les trois cartes KPI
    c1, c2, c3 = st.columns(3) # Crée 3 colonnes pour les cartes KPI
    with c1:
        render_kpi_box("Masse Salariale de l'Équipe", f"${team_total:,.0f}", f"{selected_team} — {selected_year}")
    with c2:
        render_kpi_box("Joueur le Mieux Payé", f"${top_salary:,.0f}", top_player)
    with c3:
        render_kpi_box("Meilleure Valeur (PPM+PDM+RPM par 1M$)", f"{best_value_score:.1f}", best_value_player)


    # GRAPHIQUE CIRCULAIRE (CAMEMBERT)

    # Regroupe par position avec le salaire numérique total
    df_pie = (
        df_team_year.groupby("POSITION", dropna=False, as_index=False)["SALARY_NUM"]
        .sum() # Somme les salaires par position
        .sort_values("SALARY_NUM", ascending=False) # Trie par salaire décroissant
    )

    if df_pie["SALARY_NUM"].sum() == 0 or df_pie.empty:
        st.info("Aucune donnée de salaire disponible pour cette équipe/année.") # Message si pas de données
    else:
        fig = px.pie(
            df_pie,
            names="POSITION", # Noms des tranches du camembert
            values="SALARY_NUM", # Valeurs des tranches
            title=f"Total des Salaires par Position — {selected_team} ({selected_year})", # Titre du graphique
            hole=0.35, # Taille du trou central (pour un graphique en beignet)
            color_discrete_sequence=px.colors.sequential.Blues_r # Séquence de couleurs
        )
        fig.update_traces(
            textposition="inside", # Position du texte à l'intérieur des tranches
            texttemplate="%{label}<br>$%{value:,.0f} (%{percent:.1%})", # Modèle du texte affiché
            hovertemplate="%{label}<br>Total: $%{value:,.0f}<br>%{percent}", # Modèle du texte au survol
            sort=False # Ne pas trier les tranches par Plotly (elles sont déjà triées par Pandas)
        )
        fig.update_layout(margin=dict(t=60, b=30, l=10, r=10)) # Marges du graphique
        st.plotly_chart(fig, use_container_width=True) # Affiche le graphique

        with st.expander("Afficher les lignes de joueurs pour cette saison"): # Crée un expander pour masquer/afficher les détails
            st.dataframe(
                df_team_year[["PLAYER", "POSITION", "SALARY"]], # Affiche les détails des joueurs
                hide_index=True,
                use_container_width=True
            )