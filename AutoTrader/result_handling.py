import sys
import time
import pandas as pd
import jdatetime
import os
from config import get_config


def result_handling_thread(result_queue, data, stop_event):
    config = get_config()

    """
    Thread function for handling results and logging.
    """
    folder_name = "exels"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    try:
        while not stop_event.is_set():
            time.sleep(0.01)
            if result_queue:
                result = result_queue.popleft()
                data = pd.concat([data, pd.DataFrame([result])], ignore_index=True)
                print(f"INFO: Date: {result['Date']}")
                print(f"INFO: Time: {result['Time']}")
                print(f"INFO: Underlying Avg Price: {result['avg_price_underlying']}")
                print(f"INFO: Option Avg Price: {result['avg_price_option']}")
                print(f"INFO: Black-Scholes Price: {result['black_scholes_price']}")
                print(f"INFO: Implied Volatility: {result['implied_vol']}")
                print(f"INFO: Estimated Volatility: {result['estimated_vol']}")
                print(f"INFO: Price Difference: {result['price_difference']}")
                print(f"INFO: Rolling Mean Difference: {result['rolling_mean_diff']}")
                print(f"INFO: Rolling Std Dev Difference: {result['rolling_std_diff']}")
                print(f"INFO: Z-Score: {result['z_score']}")
                print(f"INFO: Signal: {result['signal']}")
                print(f"INFO: Delta: {result['delta']}")
                print(f"INFO: Net Worth: {result['net_worth']}")
                print(f"INFO: Can Trade in Same Direction: {result['can_trade_same_dir']}")
                print(f"INFO: Risk : {result['risk']}")
                print(f"INFO: Z-Score < -{config.Z_THRESHOLD} Count: {result['under_negative_one_count']}")
                print(f"INFO: Z-Score > +{config.Z_THRESHOLD} Count: {result['over_positive_one_count']}")
                print("\n")


    finally:
        jalali_date = jdatetime.datetime.now().strftime("%Y-%m-%d")
        excel_filename = os.path.join(folder_name,
                                      f"market_name_{config.OPTION_NAME}_output_data_{jalali_date}.xlsx")
        data.to_excel(excel_filename, index=False)
        print("INFO: Data saved to Excel. result_handling_thread is shutting down gracefully.")
