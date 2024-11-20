# data_merging.py

import time
import pandas as pd
import jdatetime

def merge_historical_and_live_data(
    data_queue, historical_data_container, data, columns,
    rolling_vols, price_diff_window, processing_ready_event
):
    """
    Merges historical data with live data and initializes rolling variables.
    """
    # Only merge once
    if 'data' in historical_data_container:
        historical_data = historical_data_container.pop('data')

        # Wait until we have at least one data point from data_queue to compare timestamps
        while not data_queue:
            print("INFO: Waiting for first data point from data_queue to compare timestamps...")
            time.sleep(1)

        # Get the first timestamp from fetched data
        first_data_point = data_queue[0]
        first_data_datetime = jdatetime.datetime.strptime(
            f"{first_data_point[0].strftime('%Y-%m-%d')} {first_data_point[1].strftime('%H:%M:%S')}",
            '%Y-%m-%d %H:%M:%S'
        )

        # Convert 'Date' and 'Time' columns to datetime in historical_data
        historical_data['Datetime'] = pd.to_datetime(
            historical_data['Date'] + ' ' + historical_data['Time']
        )

        # Remove entries from historical_data where datetime is not before first_data_datetime
        while not historical_data.empty and historical_data.iloc[-1]['Datetime'] >= first_data_datetime:
            print("INFO: Removing last entry from historical_data to ensure proper merging.")
            historical_data = historical_data.iloc[:-1]

        # Drop the 'Datetime' column as it's no longer needed
        historical_data = historical_data.drop(columns=['Datetime'])

        # Merge historical data into 'data', ensuring column alignment
        if not historical_data.empty:
            # Add missing columns with NaN values if necessary
            for col in columns:
                if col not in historical_data.columns:
                    historical_data[col] = np.nan
            # Reorder columns to match 'columns' list
            historical_data = historical_data[columns]
            # Concatenate historical data with the empty 'data' DataFrame
            data = pd.concat([historical_data, data], ignore_index=True)

            # Initialize rolling_vols and price_diff_window with historical data if needed
            if 'implied_vol' in historical_data.columns:
                rolling_vols.extend(historical_data['implied_vol'].dropna().tolist())

            if 'price_difference' in historical_data.columns:
                price_diff_window.extend(historical_data['price_difference'].dropna().tolist())

            print("INFO: Historical data merged and rolling variables initialized.")

        else:
            print("WARNING: No historical data remaining after timestamp adjustment.")

        # Clear the data_queue to discard data fetched during historical data processing
        data_queue.clear()
        print("INFO: Cleared data_queue to start fresh after historical data is ready.")

        # Signal the processing thread to start
        processing_ready_event.set()
