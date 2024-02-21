from pathlib import Path


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from shiny import reactive
from shiny.express import input, render, ui
#############################################

df = pd.read_csv('NBAPlayerStats.csv')
df['REB'] = df['ORB']+df['DRB']
df['Player_Name'] = df['Player']+df['Tm']
stats_columns = ['PTS', 'AST', 'REB', 'FG%', 'TOV','STL','BLK']
players = ['LeBron James','Stephen Curry','Kevin Durant','Luka Doncic','Jayson Tatum','Joel Embiid','Nikola Jokic','Cody Zeller'] #They got the weird C's

##################################################

sns.set_theme(style="white")

ui.page_opts(fillable=True)


#def count_species(pengu, species):
 #   return df[df["Players"] == species].shape[0]


with ui.sidebar():
    #ui.input_slider("mass", "Mass", 2000, 6000, 3400)
    ui.input_checkbox_group("selected_stats", "Which stats would you like to see", list(df), selected=['PTS','REB','AST'])

    ui.input_checkbox_group("selected_players", "Filter by Player", df['Player_Name'], selected=0)
    


@reactive.Calc
def filtered_df() -> pd.DataFrame:
    filt_df = df.loc[list(map(int,input.selected_players()))]
    #filt_df = df[df["Player_Name"].isin(input.selected_players())]
    #filt_df = filt_df.loc[filt_df["Points"] > input.mass()]
    return filt_df


with ui.layout_columns():
    with ui.value_box(theme="primary"):
        "Anything"

        @render.text
        def adelie_count():
            display_df = df.loc[list(map(int,input.selected_players()))]
            return display_df['PTS'].mean().round(1)
            return "TBA"
            return count_species(filtered_df(), "Adelie")

    with ui.value_box(theme="primary"):
        "Is"

        @render.text
        def gentoo_count():
            display_df = df.loc[list(map(int,input.selected_players()))]
            return display_df['REB'].mean().round(1)
            return "TBA"
            return count_species(filtered_df(), "Gentoo")

    with ui.value_box(theme="primary"):
        "POSSIBLE"

        @render.text
        def chinstrap_count():
            display_df = df.loc[list(map(int,input.selected_players()))]
            return display_df['AST'].mean().round(1)
            return "TBA"
            return count_species(filtered_df(), "Chinstrap")


with ui.layout_columns():
    with ui.card():
        ui.card_header("Summary statistics")

        @render.data_frame
        def summary_statistics():
            #return list(map(int,input.selected_players()))
            #return df.loc[list(map(int,input.selected_players()))]
            display_df = df.loc[list(map(int,input.selected_players()))]
            return render.DataGrid(display_df, filters=True)
            #If you want to add specific filters do this one below
            display_df = filtered_df()[
                [
                    "Player",
                    "Tm",
                    "PTS",
                    "REB",
                    "AST",
                ]
            ]
            return render.DataGrid(display_df, filters=True)

    with ui.card():
        ui.card_header("Percentiles of Players")

        @render.plot
        def plot():
            players = df.loc[list(map(int,input.selected_players()))]['Player']
            players = list(map(int,input.selected_players()))
            stats_columns = list(input.selected_stats())
            create_percentile_polar_plot(df, 'Player_Name', players, stats_columns,group_column='Tm')





def create_percentile_polar_plot(data, player_column, players,stats_columns, group_column=None):
    # If a group column is provided, use it to differentiate players
    hue_order = None
    if group_column:
        hue_order = data[group_column].unique()


    percentiles_data = data[stats_columns].rank(pct=True)

# Display original DataFrame with percentiles
    #print("Original DataFrame with Percentiles:")
    #print(pd.concat([data, percentiles_data.add_suffix('_percentile')], axis=1))

# Filter specific rows while preserving percentiles
    filtered_rows = data.loc[players]

# Display filtered DataFrame with percentiles
    #print("\nFiltered DataFrame with Original Percentiles:")
    data = pd.concat([filtered_rows, percentiles_data.loc[filtered_rows.index].add_suffix('_percentile')], axis=1)

    # Create a DataFrame for polar plot
    polar_data = data[[f'{stat}_percentile' for stat in stats_columns] + [player_column, group_column]] \
        .melt(id_vars=[player_column, group_column], var_name='Stat', value_name='Percentile')

    #print(polar_data)
    # Create polar plot using seaborn
    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, polar=True)

    for player in polar_data[player_column].unique():
        player_data = polar_data[polar_data[player_column] == player]
        angles = [i / float(len(stats_columns)) * 2 * 3.14159 for i in range(len(stats_columns))]
        values = player_data['Percentile'].tolist()

        # Close the plot
        values += values[:1]
        angles += angles[:1]

        # If a group column is provided, use it for differentiation
        if group_column:
            group_value = player_data[group_column].iloc[0]
            label = f"{player} ({group_value})"
        else:
            label = player

        ax.plot(angles, values, label=label)

    # Set labels and title
    plt.autoscale(False)
    plt.xticks(angles[:-1], stats_columns)
    plt.title('Polar Comparison of Basketball Players Stats (Percentiles)')
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), title=group_column)

    return plt

