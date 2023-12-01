import os
import math
import numpy as np
import pandas as pd
from CastleDefense.data_analysis.preprocessing_data import *

processed_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_analysis/processed_data'))
combined_tracking_data_path = os.path.join(processed_data_path, 'combined_tracking_data.csv')
engineered_data_path = os.path.join(processed_data_path, 'engineered_data.csv')
test_engineered_data_path = os.path.join(processed_data_path, 'test_engineered_data.csv')

ball_carrier_tracking_data_path = os.path.join(processed_data_path, 'ball_carrier_tracking_data.csv')

velocity_engineered_data_path = os.path.join(processed_data_path, 'velocity_engineered_data.csv')
relative_features_tracking_data_path = os.path.join(processed_data_path, 'relative_features_tracking_data.csv')
extracted_features_path = os.path.join(processed_data_path, 'extracted_features.csv')


def get_engineered_data():
    """
    Returns the engineered data
    """
    return pd.read_csv(engineered_data_path)


def replace_speed_scalars_with_vectors(tracking_data):
    """
    Replaces the speed scalar with a vector
    """
    tracking_data['s_x'] = tracking_data['s'] * tracking_data['dir'].apply(lambda x: np.sin(np.radians(x)))
    tracking_data['s_y'] = tracking_data['s'] * tracking_data['dir'].apply(lambda x: np.cos(np.radians(x)))
    # tracking_data = tracking_data.drop(['s', 'dir'], axis=1)
    return tracking_data


def calculate_relative_features(tracking_data):
    ball_carrier = tracking_data[tracking_data['ball_carrier']==1]
    ball_carrier.set_index(['gameId', 'playId', 'frameId'], inplace=True, drop=True)
    playId_rusher_map = ball_carrier[['x', 'y', 's_x', 's_y']].to_dict(orient='index')

    tracking_data['ball_carrier_x'] = tracking_data.apply(
        lambda row: playId_rusher_map.get((row['gameId'], row['playId'], row['frameId']), {}).get('x', None), axis=1)
    tracking_data['ball_carrier_y'] = tracking_data.apply(
        lambda row: playId_rusher_map.get((row['gameId'], row['playId'], row['frameId']), {}).get('y', None), axis=1)
    tracking_data['ball_carrier_s_x'] = tracking_data.apply(
        lambda row: playId_rusher_map.get((row['gameId'], row['playId'], row['frameId']), {}).get('s_x', None), axis=1)
    tracking_data['ball_carrier_s_y'] = tracking_data.apply(
        lambda row: playId_rusher_map.get((row['gameId'], row['playId'], row['frameId']), {}).get('s_y', None), axis=1)

    # Calculate differences between the ball carrier and the other players:
    tracking_data['dist_x_to_ball_carrier'] = tracking_data['ball_carrier_x'] - tracking_data['x']
    tracking_data['dist_y_to_ball_carrier'] = tracking_data['ball_carrier_y'] - tracking_data['y']

    # Velocity parallel to the direction of the ball carrier:
    tracking_data['relative_s_x_to_ball_carrier'] = tracking_data['ball_carrier_s_x'] - tracking_data['s_x']
    tracking_data['relative_s_y_to_ball_carrier'] = tracking_data['ball_carrier_s_y'] - tracking_data['s_y']

    # ball_carrier_x = tracking_data['playId'].apply(lambda val: playId_rusher_map[val]['x'])
    # ball_carrier_y = tracking_data['playId'].apply(lambda val: playId_rusher_map[val]['y'])
    # ball_carrier_s_x = tracking_data['playId'].apply(lambda val: playId_rusher_map[val]['s_x'])
    # ball_carrier_s_y = tracking_data['playId'].apply(lambda val: playId_rusher_map[val]['s_y'])
    #
    # # Calculate differences between the ball carrier and the other players:
    # tracking_data['dist_x_to_ball_carrier'] = ball_carrier_x - tracking_data['x']
    # tracking_data['dist_y_to_ball_carrier'] = ball_carrier_y - tracking_data['y']
    #
    # # Velocity parallel to direction of ball carrier:
    # tracking_data['relative_s_x_to_ball_carrier'] = ball_carrier_s_x - tracking_data['s_x']
    # tracking_data['relative_s_y_to_ball_carrier'] = ball_carrier_s_y - tracking_data['s_y']

    # # Initialize new columns with zeros
    # tracking_data['dist_x_to_ball_carrier'] = 0.0
    # tracking_data['dist_y_to_ball_carrier'] = 0.0
    #
    # # Iterate over each play and frame to calculate distances
    # for (game_id, play_id), group in tracking_data.groupby(['gameId', 'playId']):
    #     for frame_id, frame_group in group.groupby('frameId'):
    #         # Get the ball carrier's position (x, y)
    #         ball_carrier_row = frame_group[frame_group['ball_carrier'] == 1]
    #         if not ball_carrier_row.empty:
    #
    #
    #             # Calculate distances for all players in the frame
    #             tracking_data.loc[(tracking_data['gameId'] == game_id) & (tracking_data['playId'] == play_id) & (
    #                     tracking_data['frameId'] == frame_id), 'dist_x_to_ball_carrier'] = frame_group['x'] - ball_carrier_row['x']
    #             tracking_data.loc[(tracking_data['gameId'] == game_id) & (tracking_data['playId'] == play_id) & (
    #                     tracking_data['frameId'] == frame_id), 'dist_y_to_ball_carrier'] = frame_group['y'] - ball_carrier_row['y']

    return tracking_data


def remove_redundant_features(tracking_data):
    redundant_features = ['gameId', 'playId', 'frameId', 'time', 'nflId', 'displayName', 'club', 'jerseyNumber', 'playDirection', 's', 'dir', 'dis', 'o','event']
    tracking_data = tracking_data.drop(redundant_features, axis=1)
    return tracking_data


# ball_carrier_tracking_data = pd.read_csv(ball_carrier_tracking_data_path)
# # tracking_data = get_combined_tracking_data()
# # velocity_tracking_data = replace_speed_scalars_with_vectors(tracking_data)
# # velocity_tracking_data.to_csv(velocity_engineered_data_path, index=False)
#
#
# velocity_tracking_data = pd.read_csv(velocity_engineered_data_path)
# relative_features_tracking_data = calculate_relative_features(velocity_tracking_data)
# relative_features_tracking_data.to_csv(relative_features_tracking_data_path, index=False)
#
# extracted_features = remove_redundant_features(relative_features_tracking_data)
# extracted_features.to_csv(extracted_features_path, index=False)

# Sanity Checks
# print('Length of ball carrier tracking data: ', len(ball_carrier_tracking_data))
# print('Length of velocity tracking data: ', len(velocity_tracking_data))
# print('Length of relative features tracking data: ', len(relative_features_tracking_data))
# print('Length of extracted features: ', len(extracted_features))