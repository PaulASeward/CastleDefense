import pandas as pd
import numpy as np
import os
import seaborn as sns
from extractPlayDataUtils import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.markers import MarkerStyle
from ipywidgets import interact, fixed
from matplotlib import animation
from math import radians
import subprocess
import IPython
from IPython.display import Video, display

import dateutil
import warnings
warnings.filterwarnings('ignore')




###################
# Create the field By:https://www.kaggle.com/code/ar2017/nfl-big-data-bowl-2021-animating-players-movement
###################
def create_football_field(linenumbers=True,
                          endzones=True,
                          highlight_line=False,
                          highlight_line_number=55,
                          highlight_first_down_line=False,
                          yards_to_go=10,
                          highlighted_name='Line of Scrimmage',
                          fifty_is_los=False,
                          figsize=(12, 6.33)):
    """
    Function that plots the football field for viewing plays.
    Allows for showing or hiding endzones.
    """
    rect = patches.Rectangle((0, 0), 120, 53.3, linewidth=0.1,
                             edgecolor='r', facecolor='darkgreen', zorder=0)

    fig, ax = plt.subplots(1, figsize=figsize)
    ax.add_patch(rect)

    plt.plot([10, 10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80,
              80, 90, 90, 100, 100, 110, 110, 120, 0, 0, 120, 120],
             [0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3,
              53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 53.3, 0, 0, 53.3],
             color='white')
    if fifty_is_los:
        plt.plot([60, 60], [0, 53.3], color='gold')
        plt.text(62, 50, '<- Player Yardline at Snap', color='gold')
    # Endzones
    if endzones:
        ez1 = patches.Rectangle((0, 0), 10, 53.3,
                                linewidth=0.1,
                                edgecolor='r',
                                facecolor='blue',
                                alpha=0.2,
                                zorder=0)
        ez2 = patches.Rectangle((110, 0), 120, 53.3,
                                linewidth=0.1,
                                edgecolor='r',
                                facecolor='blue',
                                alpha=0.2,
                                zorder=0)
        ax.add_patch(ez1)
        ax.add_patch(ez2)
    plt.xlim(0, 120)
    plt.ylim(-5, 58.3)
    plt.axis('off')
    if linenumbers:
        for x in range(20, 110, 10):
            numb = x
            if x > 50:
                numb = 120 - x
            plt.text(x, 5, str(numb - 10),
                     horizontalalignment='center',
                     fontsize=20,  # fontname='Arial',
                     color='white')
            plt.text(x - 0.95, 53.3 - 5, str(numb - 10),
                     horizontalalignment='center',
                     fontsize=20,  # fontname='Arial',
                     color='white', rotation=180)
    if endzones:
        hash_range = range(11, 110)
    else:
        hash_range = range(1, 120)

    for x in hash_range:
        ax.plot([x, x], [0.4, 0.7], color='white')
        ax.plot([x, x], [53.0, 52.5], color='white')
        ax.plot([x, x], [22.91, 23.57], color='white')
        ax.plot([x, x], [29.73, 30.39], color='white')

    if highlight_line:
        hl = highlight_line_number + 10
        plt.plot([hl, hl], [0, 53.3], color='yellow')
        plt.text(hl + 2, 50, '<- {}'.format(highlighted_name),
                color='yellow')

    if highlight_first_down_line:
        fl = hl + yards_to_go
        plt.plot([fl, fl], [0, 53.3], color='yellow')
        # plt.text(fl + 2, 50, '<- {}'.format(highlighted_name),
        #         color='yellow')
    return fig, ax


def plot_tracked_movements(ht_df, at_df, ft_df, description=None):
    """
    Plots the tracked movements from available play data.
    :param description: Description of the play
    :param ht_df:
    :param at_df:
    :param ft_df:
    :return:
    """
    play = get_play_by_id(ht_df['gameId'].iloc[0], ht_df['playId'].iloc[0])
    line_of_scrimmage, yards_to_go = get_los_details(play)
    fig, ax = create_football_field(highlight_line_number=line_of_scrimmage,
                                    highlight_line=True,
                                    highlight_first_down_line=True,
                                    yards_to_go=yards_to_go)

    ht_name = ht_df['club'].iloc[0]
    at_name = at_df['club'].iloc[0]

    ht_df.plot(x='x', y='y', kind='scatter', ax=ax, color='orange', s=30, label=ht_name)
    at_df.plot(x='x', y='y', kind='scatter', ax=ax, color='blue', s=30, label=at_name)
    ft_df.plot(x='x', y='y', kind='scatter', ax=ax, color='brown', s=30, label='football')

    gameId = ht_df['gameId'].iloc[0]
    playId = ht_df['playId'].iloc[0]

    title = f'{ht_name} vs. {at_name}: Game #{gameId} Play #{playId}'

    if description is not None:
        title += f' ({description})'

    plt.title(title)
    plt.legend()
    plt.show()


def plot_play_events(playId, gameId, week):
    """
    Plots all events for a single play.
    :param playId:
    :param gameId:
    :param week:
    :return:
    """
    play_df = load_play_data(playId, gameId, week)
    team_1, team_2, football = load_teams_from_play(play_df)

    events = play_df['event'].unique()
    events = [event for event in events if not pd.isna(event)]

    for event in events:
        ht = team_1[team_1['event'] == event]
        at = team_2[team_2['event'] == event]
        ft = football[football['event'] == event]

        plot_tracked_movements(ht, at, ft, event)


def plot_play_tracked_movements(playId, gameId, week):
    """
    Plots the tracked movements for a single play.
    :param playId:
    :param gameId:
    :param week:
    :return:
    """
    play_df = load_play_data(playId, gameId, week)
    team_1, team_2, football = load_teams_from_play(play_df)

    plot_tracked_movements(team_1, team_2, football)


###################
# Animating PLayers Movement: https://www.kaggle.com/code/ar2017/nfl-big-data-bowl-2021-animating-players-movement
###################
def animate_play(playId, gameId, week):
    """
    Animates the tracked movements for a single play.
    :param playId:
    :param gameId:
    :param week:
    :return:
    """
    fig, ax = create_football_field()
    play_df = load_play_data(playId, gameId, week)
    step_list = np.linspace(play_df['step'].min(), play_df['step'].max(), 10, dtype=int)

    marker1 = MarkerStyle(marker='x', fillstyle='full')
    marker2 = MarkerStyle(marker='o', fillstyle='full')
    # ax.scatter(row[1]['x_position'], row[1]['y_position'], marker=marker1, s=150, color='red')
    pass




gameId, playId, week = 2022090800, 343, 1
plot_play_events(playId, gameId, week)
# plot_play_tracked_movements(playId, gameId, week)
