# main.py

import time
import jdatetime
import datetime
import sys  # Add this import
from threading import Thread, Event
from collections import deque
import pandas as pd

from config import (
    UNDERLYING_TICKER, OPTION_TICKER, EXPIRATION_DATE, STRIKE_PRICE,
    RISK_FREE_RATE, CALL_PUT, SLEEP_INTERVAL, SMOOTHING_PARAM,
    WINDOW_SIZE, Z_THRESHOLD, HISTORICAL_DATA_START_DATE, HISTORICAL_DATA_END_DATE,
    SAVE_FOLDER, JUST_DOWNLOAD, VALID_TIME_START, VALID_TIME_END,
    USE_HISTORICAL
)
from trading_api import TradingAPI
from error_counters import ErrorCounters
from data_fetching import data_fetching_thread
from data_processing import processing_thread
from result_handling import result_handling_thread
# Only import historical_data_thread if USE_HISTORICAL is True
if USE_HISTORICAL:
    from historical_data import historical_data_thread

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


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
    data = pd.DataFrame(columns=columns)  # Collection for trading data

    # Initialize rolling_vols and price_diff_window
    rolling_vols = deque(maxlen=SMOOTHING_PARAM if SMOOTHING_PARAM > 1 else None)
    price_diff_window = deque(maxlen=WINDOW_SIZE)

    # Queues for inter-thread communication
    data_queue = deque()  # Queue for fetched data
    result_queue = deque()  # Queue for processed results

    # Events to signal when historical data and processing are ready
    processing_ready_event = Event()
    if USE_HISTORICAL:
        historical_data_ready_event = Event()
        historical_data_container = {}
    else:
        historical_data_ready_event = None
        historical_data_container = None

    if USE_HISTORICAL:
        # Start historical data thread
        historical_thread = Thread(target=historical_data_thread, args=(
            historical_data_ready_event, historical_data_container))
        historical_thread.daemon = True  # Set thread as daemon
        historical_thread.start()

    # Start data fetching thread
    data_thread = Thread(target=data_fetching_thread, args=(api, data_queue, counters))
    data_thread.daemon = True  # Set thread as daemon
    data_thread.start()

    # Start processing thread
    processing_thread_instance = Thread(target=processing_thread, args=(
        data_queue, result_queue, counters, processing_ready_event, rolling_vols, price_diff_window))
    processing_thread_instance.daemon = True  # Set thread as daemon
    processing_thread_instance.start()

    result_thread = None  # Placeholder for result handling thread

    try:
        # Main thread loop
        historical_data_merged = False
        while True:
            if USE_HISTORICAL:
                # Check if historical data is ready and merge data
                if historical_data_ready_event.is_set() and not historical_data_merged:
                    from data_merging import merge_historical_and_live_data

                    # Merge historical and live data, and update `data`
                    merged_data = merge_historical_and_live_data(
                        data_queue, historical_data_container, columns,
                        rolling_vols, price_diff_window, processing_ready_event
                    )
                    data = merged_data  # Update data with merged result
                    historical_data_merged = True

                    # Start result handling thread after merging data
                    result_thread = Thread(target=result_handling_thread, args=(result_queue, data))
                    result_thread.daemon = True  # Set thread as daemon
                    result_thread.start()


                    data_queue.clear()
                    print("INFO: Cleared data_queue to start fresh after historical data is ready.")

                    # Signal the processing thread to start
                    processing_ready_event.set()


            else:
                # Signal that processing can start when not using historical data
                if not processing_ready_event.is_set():
                    processing_ready_event.set()

                # Start result handling thread when not using historical data
                if result_thread is None:
                    result_thread = Thread(target=result_handling_thread, args=(result_queue, data))
                    result_thread.daemon = True  # Set thread as daemon
                    result_thread.start()

            # Check the current time against VALID_TIME_END
            current_time = jdatetime.datetime.now().time()

            if current_time > VALID_TIME_END:
                print("INFO: Current time has passed VALID_TIME_END, exiting program.")
                sys.exit()  # Exit the main thread
            time.sleep(1)
    except KeyboardInterrupt:
        print("INFO: Processing stopped by user.")
        sys.exit()  # Exit the main thread
    finally:
        # Report error counters
        counters.report()
        print("INFO: Program terminated.")



if __name__ == "__main__":
    main()
