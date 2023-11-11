import pandas as pd
import os
import numpy as np
from math import radians


def load_play_data(play_id, game_id=2022090800, week=1):
    """
    Loads tracking data for a specific play.

    Args:
        play_id (int): Play identifier.
        game_id (int, optional): Game identifier. Default is 2022090800.
        week (int, optional): Week of the season. Default is 1.

    Returns:
        pandas.DataFrame: Tracking data for the play.

    Example usage: play_data = load_play_data(12345, game_id=2022090801, week=2)
    """
    week_df = pd.read_csv(os.path.join(os.getcwd(), '../tracking_data', 'tracking_week_' + str(week) + '.csv'))
    play_df = week_df.query(f'gameId == {game_id} and playId == {play_id}')
    return play_df


def load_teams_from_play(play_df):
    """
    Extracts team data from a play DataFrame.

    Args:
        play_df (pandas.DataFrame): DataFrame with team data.

    Returns:
        tuple: DataFrames for team_1, team_2, and football.

    If exactly two teams are identified, it returns the team DataFrames.
    Otherwise, prints an error message and returns None.

    Note: Assumes non-null team names and 'football' label in the 'club' column.
    """
    teams = play_df['club'].unique()
    teams = [team for team in teams if not pd.isna(team)]

    football = play_df[play_df['club'] == 'football']
    teams = [play_df[play_df['club'] == team] for team in teams if team != 'football']

    if len(teams) != 2:
        print(f'Error: {len(teams)} teams found for play')
        return

    team_1 = teams[0]
    team_2 = teams[1]

    ##  TODO: Add Helper method to use here to sequentially order by timestep. Animation functions already have own implementation of this that triggers warnings

    ##  TODO: Add Helper method to use here so all plays are facing the same direction (Left to Right)

    return team_1, team_2, football


def get_play_by_id(gameId, playId):
    """
    Returns a play DataFrame given a gameId and playId.
    :param ht_df:
    :param gameId:
    :param playId:
    :return:
    """
    path_to_plays = os.path.join(os.getcwd(), '../overview_data', 'plays.csv')
    plays_df = pd.read_csv(path_to_plays)
    play = plays_df[(plays_df['gameId'] == gameId) & (plays_df['playId'] == playId)]

    return play


def get_los_details(play):
    """
    Extracts the line of scrimmage and yards to go from a play DataFrame.
    :param play:
    :return:
    """
    los = play['yardlineNumber'].iloc[0]
    yards_to_go = play['yardsToGo'].iloc[0]
    return los, yards_to_go


def calculate_dx_dy(x, y, angle, speed, multiplier):
    """
    Not sure if this is needed. Might be required for old data without this tracking
    :param x:
    :param y:
    :param angle:
    :param speed:
    :param multiplier:
    :return:
    """
    if angle <= 90:
        angle = angle
        dx = np.sin(radians(angle)) * multiplier * speed
        dy = np.cos(radians(angle)) * multiplier * speed
        return dx, dy
    if angle > 90 and angle <= 180:
        angle = angle - 90
        dx = np.sin(radians(angle)) * multiplier * speed
        dy = -np.cos(radians(angle)) * multiplier * speed
        return dx, dy
    if angle > 180 and angle <= 270:
        angle = angle - 180
        dx = -(np.sin(radians(angle)) * multiplier * speed)
        dy = -(np.cos(radians(angle)) * multiplier * speed)
        return dx, dy
    if angle > 270 and angle <= 360:
        angle = 360 - angle
        dx = -np.sin(radians(angle)) * multiplier * speed
        dy = np.cos(radians(angle)) * multiplier * speed
        return dx, dy
