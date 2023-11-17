import pandas as pd
import os
import numpy as np
import time
import dateutil


def load_play(playId, gameId, week=1):
    """
    Uses facade method to call other loading methods for a play
    Args:
        playId:
        gameId:
        week:
    Returns: offense, defense and football dataframes, sorted by time ascending
    """
    play = get_play_by_id(gameId, playId)
    play_df = load_play_data(playId, gameId, week)
    offense, defense, football = load_teams_from_play(play_df, play, gameId)
    return offense, defense, football


def load_play_data(play_id, game_id, week=1):
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


def load_all_plays_by_game(game_id, week):
    """
    Loads tracking data for all plays in a game.
    Args:
        game_id:
    Returns:
        pandas.DataFrame: Tracking data for the plays.
    """
    data_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tracking_data')), 'tracking_week_' + str(week) + '.csv')
    week_df = pd.read_csv(data_path)
    plays_df = week_df.query(f'gameId == {game_id}')
    return plays_df


def load_game(game_id):
    """
    Loads the game row from games.csv
    Args:
        game_id:
    Returns:
        pandas.DataFrame: Information on the game specified

    """
    path_to_games = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'overview_data')), 'games.csv')
    games_df = pd.read_csv(path_to_games)
    game_df = games_df.query(f'gameId == {game_id}')
    return game_df


def load_teams_from_play(play_df, play, gameId):
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
    game = load_game(gameId)

    home_team = game['homeTeamAbbr'].iloc[0]
    away_team = game['visitorTeamAbbr'].iloc[0]
    offense_team = play['possessionTeam'].iloc[0]
    defense_team = play['defensiveTeam'].iloc[0]

    ft_df = play_df[play_df['club'] == 'football']
    off_df = play_df[play_df['club'] == offense_team]
    def_df = play_df[play_df['club'] == defense_team]

    # Sort teams by timesteps:
    ft_df = ft_df.sort_values(by='frameId', ascending=True)
    off_df = off_df.sort_values(by='frameId', ascending=True)
    def_df = def_df.sort_values(by='frameId', ascending=True)

    #  TODO: Add Helper method to use here so all plays are facing the same direction (Left to Right)

    return off_df, def_df, ft_df


def get_play_by_id(gameId, playId):
    """
    Returns a play DataFrame given a gameId and playId.
    Args:
        gameId: identifiers to the play
        playId:
    Returns: Pandas DataFrame with the play
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


def get_los_details(play, play_df):
    """
    Extracts the line of scrimmage and yards to go from a play DataFrame.
    Args:
        play:
        play_df:
    Returns: Line of Scrimmage and Yards To Go. Both are scalar values that have been flipped to the playDirection

    """
    los = play['yardlineNumber'].iloc[0]
    yards_to_go = play['yardsToGo'].iloc[0]

    absoluteYardlineNumber = play['absoluteYardlineNumber'].item() - 10

    if (absoluteYardlineNumber > 50):
        los = 100 - los
    if (absoluteYardlineNumber <= 50):
        los = los

    if play_df['playDirection'].iloc[0] == 'left':
        yards_to_go = -yards_to_go
    else:
        yards_to_go = yards_to_go

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


def get_blocking_players(offense_df):
    """
    Returns a DataFrame with only the blocking players
    Args:
        offense_df: Should only use for Offensive team.
    """
    offense_player_ids = offense_df['nflId'].unique()
    players_df = get_players_by_ids(offense_player_ids)
    blocking_players_df = players_df[players_df['position'].isin(['TE', 'G', 'C', 'T'])]
    blocking_player_df = offense_df[offense_df['nflId'].isin(blocking_players_df['nflId'])]
    return blocking_player_df


def calculate_dx_dy(speed, angle):
    """
    Calculates the seperate x and y vectors for the speed from the player's direction
    :param angle:
    :param speed:
    :return:
    """
    angle = np.radians(angle % 360)  # Ensure angle is within [0, 360) and convert to radians

    dx = np.sin(angle) * speed  # Uses simple trigonometric identities
    dy = np.cos(angle) * speed

    if 90 < angle <= 270:
        dy = -dy

    if 180 < angle <= 360:
        dx = -dx

    return dx, dy


# gameId, playId, week = 2022090800, 343, 1
# play_df = load_play_data(gameId,playId,week)
# game = load_game(gameId)
# plays_df = load_all_plays_by_game(gameId, week)
# x=1


