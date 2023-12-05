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
    tracking_data.sort_values(by=['playId', 'gameId', 'frameId'], inplace=True)
    grouped_plays_df = tracking_data.groupby(['playId', 'gameId', 'frameId'])

    train_x = np.zeros([len(grouped_plays_df.size()), 11, 10, 10])
    # Tensor Dimensions: [A,B,C,D]
    # A: Play Frame Index =  Number of plays x Number of frames in the play
    # B: Def Player Index to calculate relative features from
    # C: 10 Offensive Players (ball-carrier omitted) to calculate relative features from
    # D: 5 Vector features - Projections on X,Y axis = size of 10

    i = 0  # Play frame index. Used to index train_x


    for (play_id, game_id, frameId), play_group in grouped_plays_df:
        offense_ids = play_group[(play_group['is_on_offense'] == 1) & (play_group['ball_carrier'] == 0)].index
        defense_ids = play_group[play_group['is_on_offense'] == 0].index

        # Iterate over defensive players, populating the tensor with respect to each defensive play for a play frame.
        for j, defense_id in enumerate(defense_ids):
            [def_x, def_y, def_Sx, def_Sy] = play_group.loc[defense_id, ['x', 'y', 's_x', 's_y']].values
            [def_rusher_x, def_rusher_y] = play_group.loc[defense_id, ['dist_x_to_ball_carrier', 'dist_y_to_ball_carrier']].values
            [def_rusher_Sx, def_rusher_Sy] = play_group.loc[defense_id, ['relative_s_x_to_ball_carrier', 'relative_s_y_to_ball_carrier']].values

            # The below code does the same as here slightly elss efficiently, but more interpretable
            # train_x[i, j, :, :4] = play_group.loc[offense_ids, ['s_x', 's_y', 'x', 'y']].values - np.array([def_Sx, def_Sy, def_x, def_y])
            # train_x[i, j, :, -6:] = [def_rusher_Sx, def_rusher_Sy, def_rusher_x, def_rusher_y, def_Sx, def_Sy]

            # The first layer of the tensor is the relative speed of the offensive players to the defensive player
            train_x[i, j, :, :2] = play_group.loc[offense_ids, ['s_x', 's_y']].values - np.array([def_Sx, def_Sy])

            # The second layer of the tensor is the relative position of the offensive players to the defensive player
            train_x[i, j, :, 2:4] = play_group.loc[offense_ids, ['x', 'y']].values - np.array([def_x, def_y])

            # The third layer of the tensor is the relative speed of the defensive player to the ball carrier
            train_x[i, j, :, 4:6] = np.array([def_rusher_Sx, def_rusher_Sy])

            # The fourth layer of the tensor is the relative position of the defensive player to the ball carrier
            train_x[i, j, :, 6:8] = np.array([def_rusher_x, def_rusher_y])

            # The fifth layer of the tensor is the speed of the defensive player
            train_x[i, j, :, 8:10] = np.array([def_Sx, def_Sy])

        i += 1

    np.save(os.path.join(processed_data_path, 'train_x_v0.npy'), train_x)


def create_tensor_train_y(tracking_data):
    """
    Creates the train_y tensor. Each frameId for each play will have size 11 x 1 representing the actual tackle made
    """
    tracking_data.sort_values(by=['playId', 'gameId', 'frameId'], inplace=True)

    train_y = tracking_data['made_tackle'].copy()

    # np.save(os.path.join(processed_data_path, 'train_y_v0.npy'), train_y)
    train_y.to_pickle(os.path.join(processed_data_path, 'train_y_v0.pkl'))


tracking_data = get_extracted_features()
print('Extracted features loaded')
create_tensor_train_x(tracking_data)
print('Train_x tensor created')
# create_tensor_train_y(tracking_data)
# print('Train_y tensor created')
