import pandas as pd
import os


def load_play_data(play_id, game_id=2022090800, week=1):
    week_df = pd.read_csv(os.path.join(os.getcwd(), 'tracking_data', 'tracking_week_' + str(week) + '.csv'))
    play_df = week_df.query(f'gameId == {game_id} and playId == {play_id}')
    return play_df
