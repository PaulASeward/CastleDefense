import pandas as pd
import os


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
    week_df = pd.read_csv(os.path.join(os.getcwd(), 'tracking_data', 'tracking_week_' + str(week) + '.csv'))
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

    return team_1, team_2, football
