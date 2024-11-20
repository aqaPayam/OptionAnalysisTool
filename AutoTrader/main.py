# main.py

import time
import pandas as pd
import numpy as np
import jdatetime
from collections import deque
from threading import Thread
import traceback

from config import (
    UNDERLYING_TICKER, OPTION_TICKER, EXPIRATION_DATE, STRIKE_PRICE,
    RISK_FREE_RATE, CALL_PUT, SLEEP_INTERVAL, SMOOTHING_PARAM,
    WINDOW_SIZE, Z_THRESHOLD, VALID_TIME_START, VALID_TIME_END
)
from trading_api import TradingAPI
from error_counters import ErrorCounters
from helpers import (
    fetch_data, validate_time_and_data, calculate_time_to_expiration,
    calculate_implied_volatility, calculate_estimated_volatility,
    calculate_black_scholes_price
)
from signals import process_price_difference, buy, sell, cancel_all_orders

def data_fetching_thread(api, data_queue, counters):
    """
    Thread function for data fetching.
    """
    while True:
        try:
            now = jdatetime.datetime.now()
            current_time = now.time()

            # Fetch data
            underlying_data, option_data = fetch_data(api, UNDERLYING_TICKER, OPTION_TICKER)

            # Put data into the queue
            data_queue.append((now, current_time, underlying_data, option_data))
            time.sleep(SLEEP_INTERVAL)
        except Exception as e:
            counters.try_except_counter += 1
            print(f"ERROR: Exception in data_fetching_thread: {e}")
            traceback.print_exc()
            time.sleep(SLEEP_INTERVAL)

def processing_thread(data_queue, result_queue, counters):
    """
    Thread function for data processing and signal generation.
    """
    # Initialize variables
    rolling_vols = deque(maxlen=SMOOTHING_PARAM if SMOOTHING_PARAM > 1 else None)
    ema_estimated_vol = np.nan  # Initial EMA value
    price_diff_window = deque(maxlen=WINDOW_SIZE)
    under_negative_one_count = 0
    over_positive_one_count = 0

    while True:
        if data_queue:
            now, current_time, underlying_data, option_data = data_queue.popleft()

            # Validate data and time
            avg_price_underlying, avg_price_option, is_valid = validate_time_and_data(
                current_time, underlying_data, option_data, counters
            )

            if not is_valid:
                print("INFO: Skipping due to invalid time or data.")
                continue

            # Calculate time to expiration
            current_date_jalali = now.strftime('%Y-%m-%d')
            time_to_expiration = calculate_time_to_expiration(current_date_jalali, EXPIRATION_DATE)
            if time_to_expiration <= 0:
                print("WARNING: Expiration date reached or passed.")
                break

            # Calculate implied volatility
            implied_vol = calculate_implied_volatility(
                avg_price_option, avg_price_underlying, time_to_expiration, STRIKE_PRICE,
                RISK_FREE_RATE, CALL_PUT, counters
            )

            # Calculate estimated volatility
            estimated_vol, rolling_vols, ema_estimated_vol = calculate_estimated_volatility(
                implied_vol, rolling_vols, ema_estimated_vol, SMOOTHING_PARAM
            )

            # Calculate Black-Scholes price
            black_scholes_price = calculate_black_scholes_price(
                avg_price_underlying, STRIKE_PRICE, RISK_FREE_RATE,
                EXPIRATION_DATE, CALL_PUT, current_date_jalali, estimated_vol
            )

            # Calculate price difference
            price_difference = avg_price_option - black_scholes_price

            # Process price difference and generate signals
            signal, under_count, over_count, rolling_mean_diff, rolling_std_diff, z_score = process_price_difference(
                price_difference, price_diff_window, WINDOW_SIZE, Z_THRESHOLD, counters
            )

            # Update counts
            under_negative_one_count += under_count
            over_positive_one_count += over_count

            # Prepare result data
            result = {
                "Date": current_date_jalali,
                "Time": now.strftime('%H:%M:%S'),
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
                "under_negative_one_count": under_negative_one_count,
                "over_positive_one_count": over_positive_one_count
            }

            # Put result into the queue
            result_queue.append(result)

            # Execute trading actions based on the signal
            if signal == 'buy':
                buy()
            elif signal == 'sell':
                sell()
            elif signal == 'hold':
                cancel_all_orders()

        else:
            time.sleep(SLEEP_INTERVAL)

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

def main():
    # Initialize API and error counters
    api = TradingAPI()
    counters = ErrorCounters()

    # Initialize DataFrame to store trading data
    columns = [
        "Date", "Time", "avg_price_underlying", "avg_price_option",
        "black_scholes_price", "implied_vol", "estimated_vol",
        "price_difference", "rolling_mean_diff", "rolling_std_diff", "z_score",
        "signal", "under_negative_one_count", "over_positive_one_count"
    ]
    data = pd.DataFrame(columns=columns)

    # Queues for inter-thread communication
    data_queue = deque()
    result_queue = deque()

    # Start threads
    threads = []

    data_thread = Thread(target=data_fetching_thread, args=(api, data_queue, counters))
    data_thread.start()
    threads.append(data_thread)

    processing_thread_instance = Thread(target=processing_thread, args=(data_queue, result_queue, counters))
    processing_thread_instance.start()
    threads.append(processing_thread_instance)

    result_thread = Thread(target=result_handling_thread, args=(result_queue, data))
    result_thread.start()
    threads.append(result_thread)

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("INFO: Processing stopped by user.")
    finally:
        # Report error counters
        counters.report()
        print("INFO: Program terminated.")

if __name__ == "__main__":
    main()
