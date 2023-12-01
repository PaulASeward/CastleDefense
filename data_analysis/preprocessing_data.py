# Joining the tracking data with the tackler/assist of a play - the variable we are predicting a probability for

import pandas as pd
import os

tracking_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tracking_data'))
processed_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_analysis/processed_data'))
tackles_data_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'overview_data')), 'tackles.csv')
combined_tracking_data_path = os.path.join(processed_data_path, 'combined_tracking_data.csv')
ball_carrier_tracking_data_path = os.path.join(processed_data_path, 'ball_carrier_tracking_data.csv')
standard_tracking_data_path = os.path.join(processed_data_path, 'standard_tracking_data.csv')
tackler_added_tracking_data_path = os.path.join(processed_data_path, 'tackler_added_tracking_data.csv')
plays_data_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'overview_data')), 'plays.csv')


def combine_tracking_weeks():
    """
    Combines all the tracking data into one csv file
    """
    list_of_csvs = sorted([f for f in os.listdir(tracking_data_path) if f.endswith(".csv")])

    for tracking_week_csv in list_of_csvs:
        tracking_week_path = os.path.join(tracking_data_path, tracking_week_csv)
        tracking_week_df = pd.read_csv(tracking_week_path)

        if tracking_week_csv == list_of_csvs[0]:
            combined_df = tracking_week_df
        else:
            combined_df = pd.concat([combined_df, tracking_week_df])
    return combined_df


def add_tackler_to_tracking_data(tracking_data):
    """
    Adds a column to the tracking data that indicates whether the player made a tackle/assist or not
    We decided to add assisted tackles since this measures the defensive player's ability to impact the ball carrier
    """
    tackles_df = pd.read_csv(tackles_data_path)

    merged_df = pd.merge(tracking_data, tackles_df, on=['gameId', 'playId'], how='left')

    # Assign 1 or 0 to each player based on whether they made a tackle or not
    tracking_data['made_tackle'] = merged_df.apply(
        lambda row: 1 if row['nflId_x'] == row['nflId_y'] and (row['tackle'] == 1 or row['assist'] == 1) else 0,
        axis=1)
    return tracking_data


def standardize_direction(tracking_data):
    """
    This should be done before standardizing the orientation.
    Flips the direction of the field so that the offense is always moving Up the field
    """
    # Rows with play_direction as 'left'
    left_direction = tracking_data['playDirection'] == 'left'

    # Apply transformations only for rows where play_direction is 'left'
    tracking_data.loc[left_direction, 'x'] = 120 - tracking_data.loc[left_direction, 'x']
    tracking_data.loc[left_direction, 'y'] = 53.3 - tracking_data.loc[left_direction, 'y']
    tracking_data.loc[left_direction, 'dir'] = (tracking_data.loc[left_direction, 'dir'] + 180) % 360
    tracking_data.loc[left_direction, 'o'] = (tracking_data.loc[left_direction, 'o'] + 180) % 360

    tracking_data = _standardize_orientation(tracking_data)

    return tracking_data


def _standardize_orientation(tracking_data):
    """
    This should be only done after standardizing the direction
    Standardizes the orientation of the field as vertical instead of horizontal
    """
    x, y = tracking_data['x'], tracking_data['y']
    tracking_data['x'] = 53.3 - y
    tracking_data['y'] = x

    tracking_data['dir'] = (tracking_data['dir'] - 90) % 360
    tracking_data['o'] = (tracking_data['o'] - 90) % 360

    return tracking_data


def add_ball_carrier_to_tracking_data(tracking_data):
    """
    Adds a column to the tracking data that indicates whether the player is the ball carrier or not
    """
    plays_df = get_plays_data()

    merged_df = pd.merge(tracking_data, plays_df, on=['gameId', 'playId'], how='left')

    tracking_data['ball_carrier'] = merged_df.apply(lambda row: 1 if row['nflId'] == row['ballCarrierId'] else 0, axis=1)

    return tracking_data


def get_combined_tracking_data():
    """
    Loads the combined tracking data
    """
    return pd.read_csv(combined_tracking_data_path)


def get_tackles_data():
    """
    Loads the tackles data
    """
    return pd.read_csv(tackles_data_path)


def get_plays_data():
    """
    Loads the plays data
    """
    return pd.read_csv(plays_data_path)


# combined_df = combine_tracking_weeks()
# combined_df.to_csv(combined_tracking_data_path, index=False)
#
# tracking_data = get_combined_tracking_data()
# tracking_data = add_tackler_to_tracking_data(tracking_data)
# tracking_data.to_csv(tackler_added_tracking_data_path, index=False)
#
# tracking_data = pd.read_csv(tackler_added_tracking_data_path)
# tracking_data = standardize_direction(tracking_data)
# tracking_data.to_csv(standard_tracking_data_path, index=False)
#
# tracking_data = pd.read_csv(standard_tracking_data_path)
# tracking_data = add_ball_carrier_to_tracking_data(tracking_data)
# tracking_data.to_csv(ball_carrier_tracking_data_path, index=False)


# # Sanity Check on df lengths
# combined_df_length = len(get_combined_tracking_data())
# tackler_added_length = len(pd.read_csv(tackler_added_tracking_data_path))
# standard_tracking_length = len(pd.read_csv(standard_tracking_data_path))
# # ball_carrier_length = len(pd.read_csv(ball_carrier_tracking_data_path))
#
# print('Combined_DF Length:', combined_df_length)
# print('Tackler Added Length:', tackler_added_length)
# print('Standard Tracking Length:', standard_tracking_length)
# # print('Ball Carrier Length:', ball_carrier_length)
