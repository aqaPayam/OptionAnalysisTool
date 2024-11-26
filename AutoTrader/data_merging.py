# data_merging.py

import time
import pandas as pd
import numpy as np  # Ensure numpy is imported

def merge_historical_and_live_data(
    data_queue, historical_data_container, columns,
    rolling_vols, price_diff_window, processing_ready_event
):
    """
    Merges historical data with live data and initializes rolling variables.

    Parameters:
    - data_queue: List of tuples containing live data points.
    - historical_data_container: Dictionary containing historical data under the 'data' key.
    - columns: List of column names to ensure alignment.
    - rolling_vols: List to store rolling implied volatilities.
    - price_diff_window: List to store rolling price differences.
    - processing_ready_event: Event to signal that processing can start.

    Historical data columns:
        - "Date"
        - "Time"
        - "avg_price_underlying"
        - "avg_price_option"
        - "implied_vol"

    DATA_QUEUE contains tuples: (current_date, current_time, underlying_data, option_data)
    """

    # Define the columns expected in the merged data
    # columns = [
    #     "Date", "Time", "avg_price_underlying", "avg_price_option",
    #     "black_scholes_price", "implied_vol", "estimated_vol",
    #     "price_difference", "rolling_mean_diff", "rolling_std_diff", "z_score",
    #     "signal", "under_negative_one_count", "over_positive_one_count"
    # ]

    if 'data' not in historical_data_container:
        print("ERROR: No historical data found in the container.")
        return

    historical_data = historical_data_container.pop('data')

    # Align historical data columns with the required structure
    for col in columns:
        if col not in historical_data.columns:
            historical_data[col] = np.nan  # Add missing columns with NaN values

    # Reorder historical data columns to match the expected structure
    historical_data = historical_data[columns]

    # Wait for at least one live data point to synchronize timestamps
    while not data_queue:
        print("INFO: Waiting for first data point from data_queue to compare timestamps...")
        time.sleep(1)

    # Extract the first live data timestamp
    first_data_point = data_queue[0]
    try:
        first_data_datetime = f"{first_data_point[0]} {first_data_point[1]}"
    except Exception as e:
        print(f"ERROR: Failed to create datetime string from data_queue: {e}")
        return

    # Filter historical data to remove entries with timestamps >= first live data timestamp
    def should_remove_last_entry():
        last_entry = historical_data.iloc[-1]
        historical_entry_datetime = f"{last_entry['Date']} {last_entry['Time']}"
        return historical_entry_datetime >= first_data_datetime

    while not historical_data.empty and should_remove_last_entry():
        print("INFO: Removing last entry from historical_data to ensure proper merging.")
        historical_data = historical_data.iloc[:-1]

    if historical_data.empty:
        print("WARNING: No historical data remaining after timestamp adjustment.")
        return

    # Merge historical data with the live data queue
    live_data_df = pd.DataFrame(data_queue, columns=columns)
    merged_data = pd.concat([historical_data, live_data_df], ignore_index=True)

    # Calculate rolling metrics
    def update_rolling_metrics(data, rolling_vols, price_diff_window):
        data['price_difference'] = data['avg_price_option'] - data['black_scholes_price']
        data['price_difference'] = data['price_difference'].apply(
            lambda x: (price_diff_window.append(x) or x) if not np.isnan(x) else (price_diff_window.append(np.nan) or np.nan)
        )
        data['implied_vol'].apply(lambda x: rolling_vols.append(x))

    update_rolling_metrics(merged_data, rolling_vols, price_diff_window)

    #TODO RIIIIDIII
    #kole diference null hast va khob begaei 
    #imp vol ama doroste kar mikone


    
    print("INFO: Historical data merged and rolling variables initialized.")

    # Clear the data_queue after merging
    data_queue.clear()

    return merged_data
