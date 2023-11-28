import os
import math
import numpy as np
import pandas as pd
from CastleDefense.data_analysis.preprocessing_data import *

processed_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_analysis/processed_data'))
combined_tracking_data_path = os.path.join(processed_data_path, 'combined_tracking_data.csv')
engineered_data_path = os.path.join(processed_data_path, 'engineered_data.csv')


def get_engineered_data():
    """
    Returns the engineered data
    """
    return pd.read_csv(engineered_data_path)


def replace_speed_scalars_with_vectors(tracking_data):
    """
    Replaces the speed scalar with a vector
    """
    tracking_data['s_x'] = -tracking_data['s'] * tracking_data['dir'].apply(lambda x: np.cos(np.radians(x+90)))
    tracking_data['s_y'] = tracking_data['s'] * tracking_data['dir'].apply(lambda x: np.sin(np.radians(x+90)))
    tracking_data = tracking_data.drop(['s', 'dir'], axis=1)
    return tracking_data


def calculate_relative_features(tracking_data):
    # Initialize new columns with zeros
    tracking_data['dist_x_to_ball_carrier'] = 0.0
    tracking_data['dist_y_to_ball_carrier'] = 0.0

    # Iterate over each play and frame to calculate distances
    for (game_id, play_id), group in tracking_data.groupby(['gameId', 'playId']):
        for frame_id, frame_group in group.groupby('frameId'):
            # Get the ball carrier's position (x, y)
            ball_carrier_row = frame_group[frame_group['nflId'] == frame_group['ball_carrier']]
            if not ball_carrier_row.empty:


                # Calculate distances for all players in the frame
                tracking_data.loc[(tracking_data['gameId'] == game_id) & (tracking_data['playId'] == play_id) & (
                        tracking_data['frameId'] == frame_id), 'dist_x_to_ball_carrier'] = frame_group['x'] - ball_carrier_row['x']
                tracking_data.loc[(tracking_data['gameId'] == game_id) & (tracking_data['playId'] == play_id) & (
                        tracking_data['frameId'] == frame_id), 'dist_y_to_ball_carrier'] = frame_group['y'] - ball_carrier_row['y']

    return tracking_data


def remove_redundant_features(tracking_data):
    redundant_features = ['gameId', 'playId', 'frameId', 'time', 'nflId', 'displayName', 'club', 'jerseyNumber', 'playDirection', 'dis', 'o','event']
    tracking_data = tracking_data.drop(redundant_features, axis=1)
    return tracking_data


tracking_data = get_combined_tracking_data()
tracking_data = replace_speed_scalars_with_vectors(tracking_data)
tracking_data.to_csv(engineered_data_path, index=False)

# tracking_data = calculate_relative_features(get_engineered_data())
# tracking_data.to_csv(engineered_data_path, index=False)

# tracking_data = remove_redundant_features(get_engineered_data())
# tracking_data.to_csv(engineered_data_path, index=False)