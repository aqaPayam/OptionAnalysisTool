import time
import pandas as pd
import jdatetime  # Importing jdatetime for Jalali date handling
import os  # Importing os for directory handling
from config import SLEEP_INTERVAL, Z_THRESHOLD

def result_handling_thread(result_queue, data):
    """
    Thread function for handling results and logging.
    """
    # Define the folder to save Excel files
    folder_name = "exels"
    
    # Ensure the folder exists
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    while True:
        if result_queue:
            result = result_queue.popleft()

            # Append data to DataFrame
            data = pd.concat([data, pd.DataFrame([result])], ignore_index=True)

            # Get today's Jalali date
            jalali_date = jdatetime.datetime.now().strftime("%Y-%m-%d")
            excel_filename = os.path.join(folder_name, f"output_data_{jalali_date}.xlsx")

            # Save DataFrame to Excel with Jalali date in the filename
            data.to_excel(excel_filename, index=False)

            # Log the results
            print(f"INFO: Underlying Avg Price: {result['avg_price_underlying']}")
            print(f"INFO: Option Avg Price: {result['avg_price_option']}")
            print(f"INFO: Implied Volatility: {result['implied_vol']}")
            print(f"INFO: Estimated Volatility: {result['estimated_vol']}")
            print(f"INFO: Black-Scholes Price: {result['black_scholes_price']}")
            print(f"INFO: Price Difference: {result['price_difference']}")
            print(f"INFO: Rolling Mean Difference: {result['rolling_mean_diff']}")
            print(f"INFO: Rolling Std Dev Difference: {result['rolling_std_diff']}")
            print(f"INFO: Z-Score: {result['z_score']}")
            print(f"INFO: Signal: {result['signal']}")
            print(f"INFO: Z-Score < -{Z_THRESHOLD} Count: {result['under_negative_one_count']}")
            print(f"INFO: Z-Score > +{Z_THRESHOLD} Count: {result['over_positive_one_count']}")
            print("\n")
        else:
            time.sleep(SLEEP_INTERVAL)
