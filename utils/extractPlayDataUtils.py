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

    data_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tracking_data')), 'tracking_week_' + str(week) + '.csv')
    week_df = pd.read_csv(data_path)
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

    path_to_plays = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'overview_data')), 'plays.csv')
    plays_df = pd.read_csv(path_to_plays)
    play = plays_df[(plays_df['gameId'] == gameId) & (plays_df['playId'] == playId)]
    return play


def get_players_by_ids(player_ids):
    """
    Returns a DataFrame with player information given a list of player ids.
    Args:
        player_ids: List of player ids
    """
    path_to_players = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'overview_data')), 'players.csv')
    players_df = pd.read_csv(path_to_players)
    player_ids_df = players_df[(players_df['nflId'].isin(player_ids))]
    return player_ids_df


def get_los_details(play):
    """
    Extracts the line of scrimmage and yards to go from a play DataFrame.
    :param play:
    :return:
    """
    los = play['yardlineNumber'].iloc[0]
    yards_to_go = play['yardsToGo'].iloc[0]
    return los, yards_to_go


def get_player_max_locations(ht_df, at_df, ft_df, padding=5):
    """
    Calculates a tuple with the min and max x and y coordinates for a play.
    Args:
        ht_df: Home team DataFrame
        at_df: Away team DataFrame
        ft_df: Football DataFrame
        padding: The amount of padding to add to the max and min coordinates

    Returns: Tuple with the min and max x and y coordinates for the play

    """
    max_x = max(ht_df['x'].max(), at_df['x'].max(), ft_df['x'].max()) + padding
    max_y = max(ht_df['y'].max(), at_df['y'].max(), ft_df['y'].max()) + padding
    min_x = min(ht_df['x'].min(), at_df['x'].min(), ft_df['x'].min()) - padding
    min_y = min(ht_df['y'].min(), at_df['y'].min(), ft_df['y'].min()) - padding

    boxed_view_coordinates = (min_x, min_y, max_x, max_y)
    return boxed_view_coordinates


def get_blocking_players(ht_df):
    offense_player_ids = ht_df['nflId'].unique()
    players_df = get_players_by_ids(offense_player_ids)
    blocking_players_df = players_df[players_df['position'].isin(['TE', 'G', 'C', 'T'])]
    blocking_player_df = ht_df[ht_df['nflId'].isin(blocking_players_df['nflId'])]
    return blocking_player_df


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
