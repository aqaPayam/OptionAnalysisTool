# main.py

import time
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

    # Initialize rolling_vols and price_diff_window
    rolling_vols = deque(maxlen=SMOOTHING_PARAM if SMOOTHING_PARAM > 1 else None)
    price_diff_window = deque(maxlen=WINDOW_SIZE)

    # Queues for inter-thread communication
    data_queue = deque()
    result_queue = deque()

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
        historical_thread.start()

    # Start data fetching thread
    data_thread = Thread(target=data_fetching_thread, args=(api, data_queue, counters))
    data_thread.start()

    # Start processing thread
    processing_thread_instance = Thread(target=processing_thread, args=(
        data_queue, result_queue, counters, processing_ready_event, rolling_vols, price_diff_window))
    processing_thread_instance.start()

    # Start result handling thread
    result_thread = Thread(target=result_handling_thread, args=(result_queue, data))
    result_thread.start()

    try:
        # Main thread loop
        historical_data_merged = False
        while True:
            if USE_HISTORICAL:
                # Check if historical data is ready and merge data
                if historical_data_ready_event.is_set() and not historical_data_merged:
                    from data_merging import merge_historical_and_live_data
                    merge_historical_and_live_data(
                        data_queue, historical_data_container, data, columns,
                        rolling_vols, price_diff_window, processing_ready_event
                    )
                    historical_data_merged = True
            else:
                # Signal that processing can start when not using historical data
                if not processing_ready_event.is_set():
                    processing_ready_event.set()
            time.sleep(1)
    except KeyboardInterrupt:
        print("INFO: Processing stopped by user.")
    finally:
        # Report error counters
        counters.report()
        print("INFO: Program terminated.")

if __name__ == "__main__":
    main()
