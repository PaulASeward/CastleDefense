import pandas as pd
import os

seperated_data_path = os.path.join(os.getcwd(), '../tracking_data', 'seperated_data')
tracking_data_path = os.path.join(os.getcwd(), '../tracking_data')

def split_tracking_data():
    list_of_csvs = sorted([f for f in os.listdir(tracking_data_path) if f.endswith(".csv")])

    for tracking_week_csv in list_of_csvs:
        tracking_week_path = os.path.join(tracking_data_path, tracking_week_csv)
        tracking_week_df = pd.read_csv(tracking_week_path)

        # Calculate the midpoint index for splitting the dataframe
        midpoint = len(tracking_week_df) // 2

        # Split the dataframe into two halves
        first_half = tracking_week_df.iloc[:midpoint]
        second_half = tracking_week_df.iloc[midpoint:]

        # Define new filenames for the two halves
        first_half_filename = tracking_week_csv.replace(".csv", "_part1.csv")
        second_half_filename = tracking_week_csv.replace(".csv", "_part2.csv")

        # Save the first and second halves as separate CSV files
        first_half.to_csv(os.path.join(seperated_data_path, first_half_filename), index=False)
        second_half.to_csv(os.path.join(seperated_data_path, second_half_filename), index=False)

        # # Delete the original CSV file
        # os.remove(tracking_week_path)


def combine_tracking_data():
    list_of_csvs = sorted([f for f in os.listdir(tracking_data_path) if f.endswith("_part1.csv")])

    for part1_csv in list_of_csvs:
        # Generate the corresponding part2 filename
        part2_csv = part1_csv.replace("_part1.csv", "_part2.csv")

        # Read both halves into dataframes
        part1_df = pd.read_csv(os.path.join(seperated_data_path, part1_csv))
        part2_df = pd.read_csv(os.path.join(seperated_data_path, part2_csv))

        # Combine both halves
        combined_df = pd.concat([part1_df, part2_df], ignore_index=True)

        # Define a new filename for the combined CSV
        combined_filename = part1_csv.replace("_part1.csv", ".csv")

        # Save the combined dataframe as a single CSV file
        combined_df.to_csv(os.path.join(tracking_data_path, combined_filename), index=False)

        # # Delete the original split files
        # os.remove(os.path.join(tracking_data_path, part1_csv))
        # os.remove(os.path.join(tracking_data_path, part2_csv))


# combine_tracking_data()
split_tracking_data()
