# main.py

import argparse
import time
import jdatetime
from threading import Thread, Event
from collections import deque
import pandas as pd

from AutoTrader.trade_condition_checking import run_trade_checker
from config import get_config, set_current_mode
from signal_handling import signal_handling_thread
from trading_api import TradingAPI
from error_counters import ErrorCounters
from data_fetching import data_fetching_thread
from data_processing import processing_thread
from result_handling import result_handling_thread

from data_merging import merge_historical_and_live_data
from historical_data import historical_data_thread

from net_worth_monitor import monitor_net_worth

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


def main():
    parser = argparse.ArgumentParser(description="Run the script with a specific configuration mode.")
    parser.add_argument('--mode', type=str, required=True,
                        help="Mode to run the script in.")
    args = parser.parse_args()

    # Set the current mode globally
    set_current_mode(args.mode)

    print(f"Loaded configuration for mode: {args.mode}")

    config = get_config()
    api = TradingAPI()
    counters = ErrorCounters()

    columns = [
        "Date", "Time", "avg_price_underlying", "avg_price_option",
        "black_scholes_price", "implied_vol", "estimated_vol",
        "price_difference", "rolling_mean_diff", "rolling_std_diff", "z_score",
        "signal", "under_negative_one_count", "over_positive_one_count"
    ]
    data = pd.DataFrame(columns=columns)

    rolling_vols = deque(maxlen=config.SMOOTHING_PARAM)
    price_diff_window = deque(maxlen=config.WINDOW_SIZE)

    data_queue = deque(maxlen=config.MAX_SIZE)
    result_queue = deque()
    signal_queue = deque(maxlen=config.MAX_SIZE)

    processing_ready_event = Event()
    stop_event = Event()  # <-- Stop event for graceful shutdown

    if config.USE_HISTORICAL:
        historical_data_ready_event = Event()
        historical_data_container = {}
    else:
        historical_data_ready_event = None
        historical_data_container = None

    # Start historical data thread if needed
    if config.USE_HISTORICAL:
        historical_thread = Thread(target=historical_data_thread, args=(
            historical_data_ready_event, historical_data_container, stop_event))
        historical_thread.start()
    else:
        historical_thread = None

    # Start trade eligibility checker thread
    trade_checker_thread = Thread(target=run_trade_checker, args=(api, stop_event))
    trade_checker_thread.start()

    # Start data fetching thread
    data_thread = Thread(target=data_fetching_thread, args=(api, data_queue, counters, stop_event))
    data_thread.start()

    # Start processing thread
    processing_thread_instance = Thread(target=processing_thread, args=(
        data_queue, result_queue, signal_queue, counters, processing_ready_event,
        rolling_vols, price_diff_window, stop_event))
    processing_thread_instance.start()

    # Start signal handling thread
    signal_thread = Thread(target=signal_handling_thread, args=(signal_queue, stop_event))
    signal_thread.start()

    # Start result handling thread (initialized later)
    result_thread = None

    # Start the net worth monitoring thread
    net_worth_thread = Thread(
        target=monitor_net_worth,
        args=(stop_event,),
        name="NetWorthMonitorThread"
    )
    net_worth_thread.start()
    print("INFO: Started net worth monitoring thread.")
    try:
        historical_data_merged = False
        while not stop_event.is_set():
            if config.USE_HISTORICAL:
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

            if current_time > config.VALID_TIME_END:
                print("INFO: Current time has passed VALID_TIME_END, initiating graceful shutdown.")
                stop_event.set()  # Signal all threads to stop
                break

            time.sleep(1)


    except KeyboardInterrupt:

        print("INFO: Processing stopped by user, initiating graceful shutdown.")

        stop_event.set()


    finally:

        net_worth_thread.join()

        print("INFO: Net worth monitoring thread has been terminated.")

        # Join other threads as necessary

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
