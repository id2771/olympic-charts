

# -*- coding: utf-8 -*-
# fichier : fonctions.py

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import pycountry


# Question : Charger les données des JO.
def charger_donnees(path_athletes, path_noc):
    """
    Charge les fichiers CSV et retourne deux DataFrames.
    """
    athletes_events = pd.read_csv(path_athletes)
    noc_regions = pd.read_csv(path_noc)
    return athletes_events, noc_regions


# Question : Nombre total + détails des médailles de Michael Phelps.
def medailles_phelps(df):
    """
    Retourne le nombre total et le détail des médailles de Michael Phelps.
    """
    phelps_data = df[df["Name"] == "Michael Fred Phelps, II"]
    total_medailles = phelps_data["Medal"].notnull().sum()
    details_medailles = phelps_data["Medal"].value_counts()
    return total_medailles, details_medailles


# Question : Nombre de nations ayant participé aux JO.
def nombre_de_nations(df):
    """
    Retourne le nombre de nations ayant participé aux JO.
    """
    return df['region'].nunique()


# Question : Qui est l'athlète le plus jeune ?
def age_minimum(df):
    """
    Retourne les athlètes les plus jeunes.
    """
    min_age = df['Age'].min()
    athletes_min_age = df[df['Age'] == min_age][[
        'Name', 'Age', 'Sex', 'Team', 'Year', 'Sport', 'Event'
    ]]
    return athletes_min_age.drop_duplicates()


# Question : Qui est l'athlète le plus âgé ?
def age_maximum(df):
    """
    Retourne les athlètes les plus âgés.
    """
    max_age = df['Age'].max()
    athletes_max_age = df[df['Age'] == max_age][[
        'Name', 'Age', 'Sex', 'Team', 'Year', 'Sport', 'Event'
    ]]
    return athletes_max_age.drop_duplicates()


# Question : Quel est le poids minimum et maximum des athlètes ?
def poids_min_max(df):
    """
    Retourne le poids minimum et maximum.
    """
    return df['Weight'].min(), df['Weight'].max()


# Question : Qui est l'athlète ayant participé le plus souvent ?
def athlete_plus_present(df):
    """
    Retourne l'athlète ayant participé le plus aux JO.
    """
    most_participated = df['Name'].value_counts().idxmax()
    participation_count = df['Name'].value_counts().max()
    return most_participated, participation_count


# Question : Classement des pays par nombre de médailles.
def calcul_medaille_pays(df):
    """
    Calcule et affiche les médailles par pays avec un graphique.
    """
    medals_df = df.dropna(subset=["Medal"])
    medal_counts = medals_df.groupby(["NOC", "Medal"]).size().unstack(fill_value=0)

    for medal in ["Gold", "Silver", "Bronze"]:
        if medal not in medal_counts.columns:
            medal_counts[medal] = 0

    medal_counts["Total"] = (
        medal_counts["Gold"] + medal_counts["Silver"] + medal_counts["Bronze"]
    )

    noc_to_team = df.drop_duplicates(subset=["NOC"])[
        ["NOC", "Team"]
    ].set_index("NOC")

    medal_counts = medal_counts.merge(
        noc_to_team, left_index=True, right_index=True
    )
    medal_counts = medal_counts.reset_index()[[
        "Team", "NOC", "Gold", "Silver", "Bronze", "Total"
    ]]
    medal_counts = medal_counts.rename(columns={"Team": "Country"})

    top_countries = medal_counts.sort_values(by="Total", ascending=False).head(10)
    countries = top_countries["Country"]
    x = range(len(countries))

    plt.figure(figsize=(12, 6))
    plt.bar(x, top_countries["Gold"], color="#FFD700", label="Gold")
    plt.bar(
        x, top_countries["Silver"], bottom=top_countries["Gold"],
        color="#C0C0C0", label="Silver"
    )
    plt.bar(
        x, top_countries["Bronze"],
        bottom=top_countries["Gold"] + top_countries["Silver"],
        color="#CD7F32", label="Bronze"
    )
    plt.xticks(x, countries, rotation=45)
    plt.ylabel("Nombre de médailles")
    plt.title("Top 10 des pays par nombre total de médailles")
    plt.legend()
    plt.tight_layout()
    plt.show()


# Question : Nombre de pays sans médailles (par type et au total).
def compter_pays_sans_medailles(df):
    """
    Affiche le nombre de pays sans médailles (total et par type).
    """
    all_countries = set(df['region'].dropna().unique())
    countries_with_any = set(
        df[df['Medal'].notna()]['region'].dropna().unique()
    )
    countries_with_gold = set(
        df[df['Medal'] == 'Gold']['region'].dropna().unique()
    )
    countries_with_silver = set(
        df[df['Medal'] == 'Silver']['region'].dropna().unique()
    )
    countries_with_bronze = set(
        df[df['Medal'] == 'Bronze']['region'].dropna().unique()
    )

    countries_without_any = all_countries - countries_with_any
    countries_without_gold = all_countries - countries_with_gold
    countries_without_silver = all_countries - countries_with_silver
    countries_without_bronze = all_countries - countries_with_bronze

    print(f"Countries without any medals: {len(countries_without_any)}")
    print(f"Countries without gold medals: {len(countries_without_gold)}")
    print(f"Countries without silver medals: {len(countries_without_silver)}")
    print(f"Countries without bronze medals: {len(countries_without_bronze)}")


# Question : Liste des pays n'ayant jamais gagné de médailles.
def lister_pays_sans_medailles(df):
    """
    Retourne la liste triée des pays n'ayant jamais gagné de médailles.
    """
    all_countries = set(df['region'].dropna().unique())
    countries_with_any = set(
        df[df['Medal'].notna()]['region'].dropna().unique()
    )
    countries_without_any = all_countries - countries_with_any
    return sorted(countries_without_any)


# Question : Carte des pays sans médailles olympiques.
def carte_pays_sans_medailles(df):
    """
    Crée une carte des pays n'ayant jamais gagné de médailles olympiques.
    """
    all_countries = set(df['region'].dropna().unique())
    countries_with_any = set(
        df[df['Medal'].notna()]['region'].dropna().unique()
    )
    countries_without_any = all_countries - countries_with_any

    df_no_medals = pd.DataFrame(list(countries_without_any), columns=["Country"])

    def get_iso_code(name):
        try:
            return pycountry.countries.lookup(name).alpha_3
        except Exception:
            return None

    df_no_medals["ISO"] = df_no_medals["Country"].apply(get_iso_code)
    df_no_medals = df_no_medals.dropna(subset=["ISO"])

    fig = px.choropleth(
        df_no_medals,
        locations="ISO",
        color_discrete_sequence=["red"],
        title="Pays n'ayant jamais gagné de médailles olympiques",
        projection="natural earth"
    )
    fig.update_geos(showcountries=True)
    fig.update_layout(showlegend=False)
    fig.show()

# Question : Carte des pays ayant gagné des médailles olympiques.
def carte_pays_avec_medailles(df):
    """
    Crée une carte des pays ayant gagné des médailles olympiques.
    """
    all_countries = set(df['region'].dropna().unique())
    countries_with_any = set(
        df[df['Medal'].notna()]['region'].dropna().unique()
    )
    countries_with_medals = all_countries - countries_with_any

    df_with_medals = pd.DataFrame(list(countries_with_medals), columns=["Country"])

    def get_iso_code(name):
        try:
            return pycountry.countries.lookup(name).alpha_3
        except Exception:
            return None

    df_with_medals["ISO"] = df_with_medals["Country"].apply(get_iso_code)
    df_with_medals = df_with_medals.dropna(subset=["ISO"])

    fig = px.choropleth(
        df_with_medals,
        locations="ISO",
        color_discrete_sequence=["blue"],
        title="Pays ayant gagné des médailles olympiques",
        projection="natural earth"
    )
    fig.update_geos(showcountries=True)
    fig.update_layout(showlegend=False)
    fig.show()
