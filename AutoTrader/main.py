# main.py

import time
import jdatetime
from threading import Thread, Event
from collections import deque
import pandas as pd

from config import get_config
from signal_handling import signal_handling_thread
from trading_api import TradingAPI
from error_counters import ErrorCounters
from data_fetching import data_fetching_thread
from data_processing import processing_thread
from result_handling import result_handling_thread

from data_merging import merge_historical_and_live_data
from historical_data import historical_data_thread

from net_worth_monitor import monitor_net_worth
from risk_management import risk_managing_thread  # Ensure risk_managing_thread is imported
from config_syncing import config_sync_thread
import argparse

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


def main():
    parser = argparse.ArgumentParser(description="Run the script with a specific configuration mode.")

    # Required arguments
    parser.add_argument('--mode', type=str, required=True, help="Mode to run the script in.")
    parser.add_argument('--underlying_name', type=str, required=True, help="Name of the underlying.")
    parser.add_argument('--underlying_ticker', type=str, required=True, help="Ticker of the underlying.")
    parser.add_argument('--option_name', type=str, required=True, help="Name of the option.")
    parser.add_argument('--option_ticker', type=str, required=True, help="Ticker of the option.")
    parser.add_argument('--expiration_date', type=str, required=True,
                        help="Expiration date of the option (YYYY-MM-DD).")
    parser.add_argument('--strike_price', type=float, required=True, help="Strike price of the option.")
    parser.add_argument('--call_put', type=str, choices=['c', 'p'], required=True,
                        help="Option type (CALL or PUT).")

    # Optional flag
    parser.add_argument('--can_trade_in_same_direction', action='store_true',
                        help="Allow trading in the same direction.")

    args = parser.parse_args()  # Parse arguments

    print(f"Mode: {args.mode}")
    print(f"Underlying Name: {args.underlying_name}")
    print(f"Underlying Ticker: {args.underlying_ticker}")
    print(f"Option Name: {args.option_name}")
    print(f"Option Ticker: {args.option_ticker}")
    print(f"Expiration Date: {args.expiration_date}")
    print(f"Strike Price: {args.strike_price}")
    print(f"Call or Put: {args.call_put}")
    print(f"Can Trade in Same Direction: {args.can_trade_in_same_direction}")

    # Get config instance
    config = get_config()

    # Set values using parsed arguments
    config.set_values(
        underlying_name=args.underlying_name,
        underlying_ticker=args.underlying_ticker,
        option_name=args.option_name,
        option_ticker=args.option_ticker,
        expiration_date=args.expiration_date,
        strike_price=args.strike_price,
        call_put=args.call_put,
        can_trade_in_same_direction=args.can_trade_in_same_direction
    )

    # Print the configuration for verification
    print(f"Configuration Set:\n"
          f"Mode: {args.mode}\n"
          f"Option Name: {config.OPTION_NAME}\n"
          f"Option Ticker: {config.OPTION_TICKER}\n"
          f"Expiration Date: {config.EXPIRATION_DATE}\n"
          f"Strike Price: {config.STRIKE_PRICE}\n"
          f"Call/Put: {config.CALL_PUT}\n"
          f"Can Trade in Same Direction: {config.CAN_TRADE_IN_SAME_DIRECTION}")

    api = TradingAPI()
    counters = ErrorCounters()

    columns = [
        "Date", "Time", "avg_price_underlying", "avg_price_option",
        "black_scholes_price", "implied_vol", "estimated_vol",
        "price_difference", "rolling_mean_diff", "rolling_std_diff", "z_score",
        "signal", "delta", "net_worth", "can_trade_same_dir", "risk", "under_negative_one_count",
        "over_positive_one_count"
    ]
    data = pd.DataFrame(columns=columns)  # kole data inja bayad bashe ta akhare code amalan

    rolling_vols = deque(
        maxlen=config.SMOOTHING_PARAM)  # ye size az inke volatility ro cheghad ghabl tar takhmin bezanim
    price_diff_window = deque(
        maxlen=config.WINDOW_SIZE)  # size panjere i ke farz mikonim price dif haye in size az N(?,?) miad

    data_queue = deque(maxlen=config.MAX_SIZE)  # data fetch mishe mire too in
    result_queue = deque()  # khorooji ha mire too in bad az process shodan
    signal_queue = deque(maxlen=config.MAX_SIZE)  # signal generate shode miad inja

    processing_ready_event = Event()  # in event miad ke process shorou beshavad ya na
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

    # Start the net worth monitoring thread
    net_worth_thread = Thread(
        target=monitor_net_worth,
        args=(stop_event,),
        name="NetWorthMonitorThread"
    )
    net_worth_thread.start()
    print("INFO: Started net worth monitoring thread.")

    # Start risk managing thread.
    risk_thread = Thread(target=risk_managing_thread, args=(api, config, stop_event))
    risk_thread.start()
    print("INFO: Started risk managing thread.")

    # Start risk managing thread.
    config_syncing = Thread(target=config_sync_thread, args=(stop_event,))
    config_syncing.start()
    print("INFO: Started config syncing thread.")

    # Start result handling thread (initialized later).
    result_thread = None

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

        if risk_thread and risk_thread.is_alive():
            risk_thread.join()

        if config_syncing and config_syncing.is_alive():
            config_syncing.join()

        counters.report()
        print("INFO: Program terminated gracefully.")


if __name__ == "__main__":
    main()
