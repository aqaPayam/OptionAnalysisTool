# result_handling.py

import time
import pandas as pd
from config import SLEEP_INTERVAL, Z_THRESHOLD

def result_handling_thread(result_queue, data):
    """
    Thread function for handling results and logging.
    """
    while True:
        if result_queue:
            result = result_queue.popleft()

            # Append data to DataFrame
            data = pd.concat([data, pd.DataFrame([result])], ignore_index=True)
            data.to_excel("output_data.xlsx", index=False)

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
