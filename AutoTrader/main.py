import time
import jdatetime
import datetime
import sys
from threading import Thread, Event
from collections import deque
import pandas as pd

from config import (
    UNDERLYING_TICKER, OPTION_TICKER, EXPIRATION_DATE, STRIKE_PRICE,
    RISK_FREE_RATE, CALL_PUT, SLEEP_INTERVAL, SMOOTHING_PARAM,
    WINDOW_SIZE, Z_THRESHOLD, HISTORICAL_DATA_START_DATE, HISTORICAL_DATA_END_DATE,
    SAVE_FOLDER, JUST_DOWNLOAD, VALID_TIME_START, VALID_TIME_END,
    USE_HISTORICAL, MAX_SIZE
)
from signal_handling import signal_handling_thread
from trading_api import TradingAPI
from error_counters import ErrorCounters
from data_fetching import data_fetching_thread
from data_processing import processing_thread
from result_handling import result_handling_thread

from data_merging import merge_historical_and_live_data
from historical_data import historical_data_thread

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


def main():
    api = TradingAPI()
    counters = ErrorCounters()

    columns = [
        "Date", "Time", "avg_price_underlying", "avg_price_option",
        "black_scholes_price", "implied_vol", "estimated_vol",
        "price_difference", "rolling_mean_diff", "rolling_std_diff", "z_score",
        "signal", "under_negative_one_count", "over_positive_one_count"
    ]
    data = pd.DataFrame(columns=columns)

    rolling_vols = deque(maxlen=SMOOTHING_PARAM)
    price_diff_window = deque(maxlen=WINDOW_SIZE)

    data_queue = deque(maxlen=MAX_SIZE)
    result_queue = deque()
    signal_queue = deque(maxlen=MAX_SIZE)

    processing_ready_event = Event()
    stop_event = Event()  # <-- Stop event for graceful shutdown

    if USE_HISTORICAL:
        historical_data_ready_event = Event()
        historical_data_container = {}
    else:
        historical_data_ready_event = None
        historical_data_container = None

    # Start historical data thread if needed
    if USE_HISTORICAL:
        historical_thread = Thread(target=historical_data_thread, args=(
            historical_data_ready_event, historical_data_container, stop_event))
        historical_thread.start()
    else:
        historical_thread = None

    # Start data fetching thread
    data_thread = Thread(target=data_fetching_thread, args=(api, data_queue, counters, stop_event))
    data_thread.start()

    # Start processing thread
    processing_thread_instance = Thread(target=processing_thread, args=(
        data_queue, result_queue, signal_queue, counters, processing_ready_event,
        rolling_vols, price_diff_window, stop_event))
    processing_thread_instance.start()

    signal_thread = Thread(target=signal_handling_thread, args=(signal_queue, stop_event))
    signal_thread.start()

    result_thread = None

    try:
        historical_data_merged = False
        while not stop_event.is_set():
            if USE_HISTORICAL:
                if historical_data_ready_event.is_set() and not historical_data_merged:
                    data = merge_historical_and_live_data(
                        data_queue, historical_data_container, columns,
                        rolling_vols, price_diff_window, processing_ready_event, counters
                    )
                    historical_data_merged = True

                    result_thread = Thread(target=result_handling_thread, args=(result_queue, data, stop_event))
                    result_thread.start()

                    data_queue.clear()
                    print("INFO: Cleared data_queue to start fresh after historical data is ready.")
                    processing_ready_event.set()
            else:
                if not processing_ready_event.is_set():
                    processing_ready_event.set()

                if result_thread is None:
                    result_thread = Thread(target=result_handling_thread, args=(result_queue, data, stop_event))
                    result_thread.start()

            current_time = jdatetime.datetime.now().time()

            if current_time > VALID_TIME_END:
                print("INFO: Current time has passed VALID_TIME_END, initiating graceful shutdown.")
                stop_event.set()  # Signal all threads to stop
                break

            time.sleep(1)

    except KeyboardInterrupt:
        print("INFO: Processing stopped by user, initiating graceful shutdown.")
        stop_event.set()
    finally:
        # Wait for all threads to finish
        if historical_thread and historical_thread.is_alive():
            historical_thread.join()

        if data_thread.is_alive():
            data_thread.join()

        if processing_thread_instance.is_alive():
            processing_thread_instance.join()

        if signal_thread.is_alive():
            signal_thread.join()

        if result_thread and result_thread.is_alive():
            result_thread.join()

        counters.report()
        print("INFO: Program terminated gracefully.")


if __name__ == "__main__":
    main()
