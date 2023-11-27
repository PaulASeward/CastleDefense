# Joining the tracking data with when the tackle is made - the variable we are predicting a probability for

import pandas as pd
import os

tracking_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tracking_data'))
processed_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_analysis/processed_data'))
tackles_data_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'overview_data')), 'tackles.csv')
combined_tracking_data_path = os.path.join(processed_data_path, 'combined_tracking_data.csv')


def add_tackler_to_tracking_data():
    """
    Adds a column to the tracking data that indicates whether the player made a tackle/assist or not
    We decided to add assisted tackles since this measures the defensive player's ability to impact the ball carrier
    """
    # Importing the tracking data
    list_of_csvs = sorted([f for f in os.listdir(tracking_data_path) if f.endswith(".csv")])

    for tracking_week_csv in list_of_csvs:
        tracking_week_path = os.path.join(tracking_data_path, tracking_week_csv)
        processed_week_path = os.path.join(processed_data_path, tracking_week_csv)

        tracking_week_df = pd.read_csv(tracking_week_path)
        tackles_df = pd.read_csv(tackles_data_path)
        merged_df = pd.merge(tracking_week_df, tackles_df, on=['gameId', 'playId'], how='left')

        # Assign 1 or 0 to each player based on whether they made a tackle or not
        tracking_week_df['made_tackle'] = merged_df.apply(lambda row: 1 if row['nflId_x'] == row['nflId_y'] and (row['tackle'] == 1 or row['assist']==1) else 0,
                                                          axis=1)

        tracking_week_df.to_csv(processed_week_path, index=False)

        print(len(tracking_week_df))



def combine_tracking_weeks():
    """
    Combines all the tracking data into one csv file
    """
    list_of_csvs = sorted([f for f in os.listdir(processed_data_path) if f.endswith(".csv")])

    for tracking_week_csv in list_of_csvs:
        tracking_week_path = os.path.join(processed_data_path, tracking_week_csv)
        tracking_week_df = pd.read_csv(tracking_week_path)

        if tracking_week_csv == list_of_csvs[0]:
            combined_df = tracking_week_df
        else:
            combined_df = pd.concat([combined_df, tracking_week_df])

    combined_df.to_csv(combined_tracking_data_path, index=False)


# add_tackler_to_tracking_data()
# combine_tracking_weeks()