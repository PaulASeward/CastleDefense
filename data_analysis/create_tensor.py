import numpy as np
import os
import pandas as pd
from CastleDefense.data_analysis.preprocessing_data import get_plays_data
from CastleDefense.data_analysis.feature_extraction import get_extracted_features

processed_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_analysis/processed_data'))


def create_tensor_train_x(tracking_data):
    """
    Creates the train_x tensor
    """
    df_play = get_plays_data()
    df_play.sort_values(by=['playId', 'gameId'], inplace=True)
    tracking_data.sort_values(by=['playId', 'gameId'], inplace=True)

    grouped_plays_df = tracking_data.groupby(['playId', 'gameId'])
    train_x = np.zeros([len(grouped_plays_df.size()), 11, 10, 10])
    i = 0
    play_ids = df_play[['playId', 'gameId']].values

    for (play_id, game_id), play_group in grouped_plays_df:
        if (play_id, game_id) != tuple(play_ids[i]):
            print("Error:", (play_id, game_id), tuple(play_ids[i]))

        # [[rusher_x, rusher_y, rusher_Sx, rusher_Sy]] = play_group.loc[play_group.ball_carrier == 1, ['x', 'y', 's_x', 's_y']].values

        offense_ids = play_group[play_group.is_on_offense & ~play_group.ball_carrier].index
        defense_ids = play_group[~play_group.is_on_offense].index

        for j, defense_id in enumerate(defense_ids):
            [def_x, def_y, def_Sx, def_Sy] = play_group.loc[defense_id, ['x', 'y', 's_x', 's_y']].values
            [def_rusher_x, def_rusher_y] = play_group.loc[defense_id, ['dist_x_to_ball_carrier', 'dist_y_to_ball_carrier']].values
            [def_rusher_Sx, def_rusher_Sy] = play_group.loc[
                defense_id, ['relative_s_x_to_ball_carrier', 'relative_s_y_to_ball_carrier']].values

            train_x[i, j, :, :4] = play_group.loc[offense_ids, ['s_x', 's_y', 'x', 'y']].values - np.array(
                [def_Sx, def_Sy, def_x, def_y])
            train_x[i, j, :, -6:] = [def_rusher_Sx, def_rusher_Sy, def_rusher_x, def_rusher_y, def_Sx, def_Sy]

        i += 1

    np.save(os.path.join(processed_data_path, 'train_x_v0.npy'), train_x)


def create_tensor_train_y(tracking_data):
    """
    Creates the train_y tensor. Each frameId for each play will have size 11 x 1 representing the actual tackle made
    """
    tracking_data.sort_values(by=['playId'], inplace=True)

    train_y = tracking_data['made_tackle'].copy()

    # np.save(os.path.join(processed_data_path, 'train_y_v0.npy'), train_y)
    train_y.to_pickle(os.path.join(processed_data_path, 'train_y_v0.pkl'))



tracking_data = get_extracted_features()
print('Extracted features loaded')
create_tensor_train_x(tracking_data)
print('Train_x tensor created')