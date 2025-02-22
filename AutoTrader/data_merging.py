# data_merging.py
import time
import pandas as pd
import numpy as np

from helpers import (
    validate_time_and_data, calculate_time_to_expiration,
    calculate_implied_volatility, calculate_estimated_volatility,
    calculate_black_scholes_price, validate_time_and_data_preprocess,
    calculate_delta, update_signal  # Added Delta import
)
from signals import process_price_difference
from config import get_config


def merge_historical_and_live_data(
        data_queue, historical_data_container, columns,
        rolling_vols, price_diff_window, processing_ready_event,
        counters
):
    config = get_config()
    """
    Merges historical data with live data and initializes rolling variables.
    Then applies the same processing steps (implied_vol, estimated_vol,
    black_scholes_price, signals) to both the historical data (after trimming)
    and the live data until the data_queue is empty.

    Parameters:
    - data_queue: Deque or list of tuples (current_date_jalali, current_time, underlying_data, option_data).
    - historical_data_container: Dictionary containing historical data under 'data' key.
    - columns: List of column names to ensure alignment.
    - rolling_vols: List to store rolling implied volatilities.
    - price_diff_window: List to store rolling price differences.
    - processing_ready_event: Event to signal that processing can start.
    - counters: Dictionary or similar structure for tracking counts and other metrics.

    Returns:
    A pandas DataFrame containing fully processed historical and live data.
    """

    if 'data' not in historical_data_container:
        print("ERROR: No historical data found in the container.")
        return

    historical_data = historical_data_container.pop('data')

    # Ensure all required columns are present
    for col in columns:
        if col not in historical_data.columns:
            historical_data[col] = np.nan

    # Reorder columns
    historical_data = historical_data[columns]

    # Wait until we have at least one live data point
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

    # Function to determine if the last historical entry is too recent
    def should_remove_last_entry():
        if historical_data.empty:
            return False
        last_entry = historical_data.iloc[-1]
        historical_entry_datetime = f"{last_entry['Date']} {last_entry['Time']}"
        return historical_entry_datetime >= first_data_datetime

    # Remove overlapping or too-recent historical entries
    while not historical_data.empty and should_remove_last_entry():
        print("INFO: Removing last entry from historical_data to ensure proper merging.")
        historical_data = historical_data.iloc[:-1]

    if historical_data.empty:
        print("WARNING: No historical data remaining after timestamp adjustment.")
        # Even if no historical data remains, we can still process live data as is.
        # But let's proceed with just the live data in that case.
        pass

    # Initialize counters for signals
    under_negative_one_count = 0
    over_positive_one_count = 0

    # Process historical data first
    processed_rows = []
    for idx, row in historical_data.iterrows():
        current_date_jalali = row["Date"]
        current_time = row["Time"]
        avg_price_underlying = row["avg_price_underlying"]
        avg_price_option = row["avg_price_option"]

        # Validate data
        is_valid = validate_time_and_data_preprocess(
            current_time, avg_price_underlying, avg_price_option, counters
        )
        if not is_valid:
            # Skip invalid historical rows
            continue

        # Calculate time to expiration
        time_to_expiration = calculate_time_to_expiration(current_date_jalali, config.EXPIRATION_DATE)
        if time_to_expiration <= 0:
            # Skip rows that are past expiration
            continue

        # Implied volatility
        implied_vol = calculate_implied_volatility(
            avg_price_option, avg_price_underlying, time_to_expiration, config.STRIKE_PRICE,
            config.RISK_FREE_RATE, config.CALL_PUT, counters
        )

        # Estimated volatility
        estimated_vol = calculate_estimated_volatility(implied_vol, rolling_vols)

        # Black-Scholes price
        black_scholes_price = calculate_black_scholes_price(
            avg_price_underlying, config.STRIKE_PRICE, config.RISK_FREE_RATE,
            config.EXPIRATION_DATE, config.CALL_PUT, current_date_jalali, estimated_vol
        )

        # Price difference
        price_difference = avg_price_option - black_scholes_price

        # **Delta Calculation**
        delta = calculate_delta(
            avg_price_underlying, config.STRIKE_PRICE, time_to_expiration,
            config.RISK_FREE_RATE, estimated_vol, config.CALL_PUT
        )

        # Process price difference for signals
        signal, under_count, over_count, rolling_mean_diff, rolling_std_diff, z_score = process_price_difference(
            price_difference, price_diff_window, config.WINDOW_SIZE, config.Z_THRESHOLD, counters
        )
        signal = update_signal(signal, delta, config)

        # Update counts
        under_negative_one_count += under_count
        over_positive_one_count += over_count

        # Update the row with computed values
        row["black_scholes_price"] = black_scholes_price
        row["implied_vol"] = implied_vol
        row["estimated_vol"] = estimated_vol
        row["price_difference"] = price_difference
        row["rolling_mean_diff"] = rolling_mean_diff
        row["rolling_std_diff"] = rolling_std_diff
        row["z_score"] = z_score
        row["signal"] = signal
        row["delta"] = delta  # Added Delta to results
        row["under_negative_one_count"] = under_negative_one_count
        row["over_positive_one_count"] = over_positive_one_count

        processed_rows.append(row)

    historical_data = pd.DataFrame(processed_rows, columns=columns)

    # Now process live data until the data_queue is empty
    live_processed_rows = []
    while data_queue:
        current_date_jalali, current_time, underlying_data, option_data = data_queue.popleft()

        # Validate data and time
        avg_price_underlying, avg_price_option, is_valid = validate_time_and_data(
            current_time, underlying_data, option_data, counters
        )
        if not is_valid:
            print("INFO: Skipping due to invalid data or time: data has 0 or invalid conditions.")
            continue

        # Calculate time to expiration
        time_to_expiration = calculate_time_to_expiration(current_date_jalali, config.EXPIRATION_DATE)
        if time_to_expiration <= 0:
            print("WARNING: Expiration date reached or passed.")
            # Stop processing since expiration is passed
            break

        # Calculate implied volatility
        implied_vol = calculate_implied_volatility(
            avg_price_option, avg_price_underlying, time_to_expiration, config.STRIKE_PRICE,
            config.RISK_FREE_RATE, config.CALL_PUT, counters
        )

        # Calculate estimated volatility
        estimated_vol = calculate_estimated_volatility(implied_vol, rolling_vols)

        # Calculate Black-Scholes price
        black_scholes_price = calculate_black_scholes_price(
            avg_price_underlying, config.STRIKE_PRICE, config.RISK_FREE_RATE,
            config.EXPIRATION_DATE, config.CALL_PUT, current_date_jalali, estimated_vol
        )

        # Calculate price difference
        price_difference = avg_price_option - black_scholes_price

        # **Delta Calculation**
        delta = calculate_delta(
            avg_price_underlying, config.STRIKE_PRICE, time_to_expiration,
            config.RISK_FREE_RATE, estimated_vol, config.CALL_PUT
        )

        # Process price difference and generate signals
        signal, under_count, over_count, rolling_mean_diff, rolling_std_diff, z_score = process_price_difference(
            price_difference, price_diff_window, config.WINDOW_SIZE, config.Z_THRESHOLD, counters
        )
        signal = update_signal(signal, delta, config)

        # Update counts
        under_negative_one_count += under_count
        over_positive_one_count += over_count

        # Prepare result data as a dictionary
        live_result = {
            "Date": current_date_jalali,
            "Time": current_time,
            "avg_price_underlying": avg_price_underlying,
            "avg_price_option": avg_price_option,
            "black_scholes_price": black_scholes_price,
            "implied_vol": implied_vol,
            "estimated_vol": estimated_vol,
            "price_difference": price_difference,
            "rolling_mean_diff": rolling_mean_diff,
            "rolling_std_diff": rolling_std_diff,
            "z_score": z_score,
            "signal": signal,
            "delta": delta,  # Added Delta to results
            "under_negative_one_count": under_negative_one_count,
            "over_positive_one_count": over_positive_one_count,

        }

        live_processed_rows.append(live_result)

    live_data = pd.DataFrame(live_processed_rows, columns=columns)

    # Combine processed historical and live data
    # If historical_data is empty, it will just return live_data
    combined_data = pd.concat([historical_data, live_data], ignore_index=True)

    # Signal that processing is now fully ready since we have a combined dataset
    processing_ready_event.set()

    return combined_data
