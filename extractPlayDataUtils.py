import pandas as pd
import os


def load_play_data(play_id, week=1, game_id=2022090800):
    week_df = pd.read_csv(os.path.join(os.getcwd(), 'tracking_data', 'tracking_week_' + str(week) + '.csv'))
    play_df = week_df[week_df['playId'] == play_id]
    return play_df
