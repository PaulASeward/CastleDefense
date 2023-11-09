import pandas as pd
import numpy as np
import os
import seaborn as sns
from extractPlayDataUtils import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# train = pd.read_csv('../input/nfl-big-data-bowl-2020/train.csv', low_memory=False)
# train2021 = pd.read_csv('../input/nfl-big-data-bowl-2021/plays.csv')


###################
# Create the field By: https://www.kaggle.com/code/aryashah2k/sports-analytics-visualization
###################
def create_football_field():
    # Create a rectangle defined via an anchor point *xy* and its *width* and *height*
    rect = patches.Rectangle((0, 0), 120, 53.3, facecolor='green', zorder=0)

    ###################
    # Other color info: https://matplotlib.org/stable/gallery/color/named_colors.html
    ###################

    # Creating a subplot to plot our field on
    fig, ax = plt.subplots(1, figsize=(12, 6.33))

    # Adding the rectangle to the plot
    ax.add_patch(rect)

    # Plotting a line plot for marking the field lines
    plt.plot([10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80,
              80, 90, 90, 100, 100, 110, 110, 120, 0, 0, 120, 120],
             [0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3,
              0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 53.3, 0, 0, 53.3],
             color='white', zorder=0)

    # Creating the left end-zone
    left_end_zone = patches.Rectangle((0, 0), 10, 53.3, facecolor='blue', alpha=0.2, zorder=0)

    # Creating the right end-zone
    right_end_zone = patches.Rectangle((110, 0), 120, 53.3, facecolor='blue', alpha=0.2, zorder=0)

    # Adding the patches to the subplot
    ax.add_patch(left_end_zone)
    ax.add_patch(right_end_zone)

    # Setting the limits of x-axis from 0 to 120
    plt.xlim(0, 120)

    # Setting the limits of y-axis from -5 to 58.3
    plt.ylim(-5, 58.3)

    # Removing the axis values from the plot
    plt.axis('off')

    # Plotting the numbers starting from x = 20 and ending at x = 110
    # with a step of 10
    for x in range(20, 110, 10):

        # Intializing another variable named 'number'
        number = x

        # If x exceeds 50, subtract it from 120
        if x > 50:
            number = 120 - x

        # Plotting the text at the bottom
        plt.text(x, 5, str(number - 10),
                 horizontalalignment='center',
                 fontsize=20,
                 color='white')

        # Plotting the text at the top
        plt.text(x - 0.95, 53.3 - 5, str(number - 10),
                 horizontalalignment='center',
                 fontsize=20,
                 color='white',
                 rotation=180)

    # Making ground markings
    for x in range(11, 110):
        ax.plot([x, x], [0.4, 0.7], color='white', zorder=0)
        ax.plot([x, x], [53.0, 52.5], color='white', zorder=0)
        ax.plot([x, x], [22.91, 23.57], color='white', zorder=0)
        ax.plot([x, x], [29.73, 30.39], color='white', zorder=0)

    # Returning the figure and axis
    return fig, ax



###################
# Plot the play By: https://www.kaggle.com/code/aryashah2k/sports-analytics-visualization
###################
def plot_single_play_events(playId, gameId, week):
    play_df = load_play_data(playId, gameId, week)

    teams = play_df['club'].unique()
    teams = [team for team in teams if not pd.isna(team)]

    football = play_df[play_df['club'] == 'football']
    teams = [play_df[play_df['club'] == team] for team in teams if team != 'football']

    if len(teams) != 2:
        print(f'Error: {len(teams)} teams found for playId {playId} gameId {gameId} week {week}')
        return

    team_1 = teams[0]
    team_2 = teams[1]

    team_1_name = team_1['club'].iloc[0]
    team_2_name = team_2['club'].iloc[0]

    team_1_color = 'orange'
    team_2_color = 'blue'

    home_team = play_df[play_df['club'] == 'LA']
    away_team = play_df[play_df['club'] == 'BUF']

    events = play_df['event'].unique()
    events = [event for event in events if not pd.isna(event)]

    for event in events:
        ht = home_team[home_team['event'] == event]
        at = away_team[away_team['event'] == event]
        ft = football[football['event'] == event]

        if (not ht.empty) and (not at.empty) :
            fig, ax = create_football_field()
            ht.plot(x='x', y='y', kind='scatter', ax=ax, color=team_1_color, s=30, label=team_1_name)
            at.plot(x='x', y='y', kind='scatter', ax=ax, color=team_2_color, s=30, label=team_2_name)
            ft.plot(x='x', y='y', kind='scatter', ax=ax, color='brown', s=30, label='football')

            plt.title(f'Game #{gameId} Play #{playId} Week #{week} at {event}')
            plt.legend()
            plt.show()


# create_football_field()
# plt.show()

gameId = 2022090800
playId = 343
week = 1

plot_single_play_events(playId, gameId, week)


