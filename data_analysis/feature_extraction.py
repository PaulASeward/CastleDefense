import os
import math
import numpy as np
import pandas as pd
from CastleDefense.utils.extractPlayDataUtils import load_all_plays_by_game
from CastleDefense.data_analysis.preprocessing_data import *
from CastleDefense.data_analysis.model_predictions import use_model_to_predict_tackler

processed_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_analysis/processed_data'))
combined_tracking_data_path = os.path.join(processed_data_path, 'combined_tracking_data.csv')
engineered_data_path = os.path.join(processed_data_path, 'engineered_data.csv')
test_engineered_data_path = os.path.join(processed_data_path, 'test_engineered_data.csv')

ball_carrier_tracking_data_path = os.path.join(processed_data_path, 'ball_carrier_tracking_data.csv')

velocity_engineered_data_path = os.path.join(processed_data_path, 'velocity_engineered_data.csv')
relative_features_tracking_data_path = os.path.join(processed_data_path, 'relative_features_tracking_data.csv')
extracted_features_path = os.path.join(processed_data_path, 'extracted_features.csv')
tracking_data_all_features_path = os.path.join(processed_data_path, 'tracking_data_all_features.csv')

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

    return tracking_data


def remove_redundant_features(tracking_data):
    tracking_data = tracking_data[tracking_data['club'] != 'football']
    redundant_features = ['time', 'nflId', 'displayName', 'club', 'jerseyNumber', 'playDirection', 's', 'dir', 'dis', 'o','event']
    tracking_data = tracking_data.drop(redundant_features, axis=1)
    return tracking_data


def extract_features(tracking_data):
    tracking_data = replace_speed_scalars_with_vectors(tracking_data)
    tracking_data = calculate_relative_features(tracking_data)
    tracking_data = remove_redundant_features(tracking_data)
    return tracking_data


def get_extracted_features():
    return pd.read_csv(extracted_features_path)


def append_predicted_tackler(tracking_data, y_pred):
    # Create empty new column for predicted tackler
    tracking_data['predicted_tackler'] = np.zeros(len(tracking_data))

    grouped_frames_df = tracking_data.groupby(['frameId'])
    for frame_id, frame_group in grouped_frames_df:
        defense_ids = frame_group[frame_group['is_on_offense'] == 0].index

        for i, defense_id in enumerate(defense_ids):
            tracking_data.loc[defense_id, 'predicted_tackler'] = y_pred[frame_id-1][i]

    return tracking_data


def extract_predicted_tackler(tracking_data):
    tracking_data = process_data(tracking_data)
    tracking_data = extract_features(tracking_data)
    x_train, y_pred = use_model_to_predict_tackler(tracking_data)
    tracking_data = append_predicted_tackler(tracking_data, y_pred)
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


# relative_features = pd.read_csv(relative_features_tracking_data_path)
# print('Read relative features')
#
# offense_label = add_offense_label(relative_features)
# print('Added offense label')
# offense_label.to_csv(extracted_features_path, index=False)
#
# tracking_data_all_features = pd.read_csv(tracking_data_all_features_path)
# print('Read offense label')
# extracted_features = remove_redundant_features(tracking_data_all_features)
# print('Removed redundant features')
# extracted_features.to_csv(extracted_features_path, index=False)
# print(extracted_features.head(10))

# gameId, playId, week = 2022101609, 2504, 6
# play_df = load_all_plays_by_game(gameId, week)
# # play_df = load_play_data(gameId,playId,week)
# play_df = extract_predicted_tackler(play_df)