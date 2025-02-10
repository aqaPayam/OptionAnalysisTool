# signals.py

import numpy as np
from collections import deque
from typing import Tuple

from trading_api import TradingAPI
from error_counters import ErrorCounters
from config import get_config


def generate_signals(z_score: float, z_threshold: float) -> Tuple[str, float, float]:
    """
    Generate buy/sell/hold signals based on z-score thresholds.

    Args:
        z_score (float): Calculated z-score.
        z_threshold (float): Threshold for z-score to trigger signals.

    Returns:
        Tuple[str, float, float]: Signal ('buy', 'sell', 'hold'), under_count, over_count.
    """
    if np.isnan(z_score):
        return 'hold', 0, 0  # Invalid z_score, hold

    if z_score < -z_threshold:
        return 'buy', 1, 0
    elif z_score > z_threshold:
        return 'sell', 0, 1
    else:
        return 'hold', 0, 0


def process_price_difference(price_difference, price_diff_window, window_size, z_threshold, counters):
    """
    Process the price difference, generate signals, calculate rolling statistics, and update rolling window.

    Args:
        price_difference (float): Current price difference.
        price_diff_window (deque): Rolling window of past price differences.
        window_size (int): The size of the rolling window.
        z_threshold (float): Threshold for z-score to trigger signals.
        counters (ErrorCounters): An instance of the ErrorCounters class.

    Returns:
        Tuple[str, float, float, float, float, float]: Signal, under_count, over_count, rolling_mean_diff, rolling_std_diff, z_score.
    """
    try:
        # Calculate rolling statistics based on existing window (excluding current price_difference)
        if len(price_diff_window) >= window_size:
            rolling_mean_diff = np.mean(price_diff_window)
            rolling_std_diff = np.std(price_diff_window, ddof=1)
            if rolling_std_diff == 0:
                z_score = 0.0  # or some default value
            else:
                z_score = (price_difference - rolling_mean_diff) / rolling_std_diff

            # Generate signal based on z-score
            signal, under_count, over_count = generate_signals(z_score, z_threshold)
        else:
            # Not enough data for rolling statistics
            rolling_mean_diff = np.nan
            rolling_std_diff = np.nan
            z_score = np.nan
            signal = 'hold'
            under_count = 0
            over_count = 0
            # Count as condition-related error
            counters.condition_error_counter += 1

        # Append the new price_difference to the window AFTER signal generation
        if not np.isnan(price_difference):
            price_diff_window.append(price_difference)

        return signal, under_count, over_count, rolling_mean_diff, rolling_std_diff, z_score

    except Exception as e:
        print(f"ERROR: Error in processing price difference: {e}")
        counters.try_except_counter += 1
        return 'hold', 0, 0, np.nan, np.nan, np.nan


def buy():
    config = get_config()
    if config.NET_WORTH > 0:
        print(f"Net worth buy (${config.NET_WORTH}) exceeds the maximum bid (${config.MAX_BID}).")
        return

    """
    Implements the buy logic using the TradingAPI.
    """
    print("INFO: Executing Buy Order")

    api = TradingAPI()

    # Calculate buy price
    market_data = api.fetch_order_book(config.OPTION_TICKER)
    if market_data and market_data[2]:
        best_bid_price = market_data[2]
        buy_price = best_bid_price + config.BUY_PRICE_OFFSET
    else:
        print("WARNING: Could not fetch market data for buy price calculation.")
        return

    order_quantity = max(1, config.ORDER_PRICE // buy_price)
    # Place or modify buy order
    api.buy(ticker=config.OPTION_TICKER, price=buy_price, quantity=order_quantity)


def sell():
    config = get_config()
    if config.NET_WORTH < 0:
        print(f"Net worth sell (${config.NET_WORTH}) exceeds the maximum bid (${config.MAX_BID}).")
        return
    """
    Implements the sell logic using the TradingAPI.
    """
    print("INFO: Executing Sell Order")

    api = TradingAPI()

    # Calculate sell price
    market_data = api.fetch_order_book(config.OPTION_TICKER)
    if market_data and market_data[1]:
        best_ask_price = market_data[1]
        sell_price = best_ask_price + config.SELL_PRICE_OFFSET
    else:
        print("WARNING: Could not fetch market data for sell price calculation.")
        return



    order_quantity = max(1, config.ORDER_PRICE // sell_price)
    # Place or modify sell order
    api.sell(ticker=config.OPTION_TICKER, price=sell_price, quantity=order_quantity)


def cancel_all_orders():
    config = get_config()
    """
    Cancels all open orders for the specified ticker.
    """
    print("INFO: Cancelling all open orders.")

    api = TradingAPI()
    open_orders = api.fetch_open_orders()
    if open_orders:
        # Filter orders for the specific ticker
        ticker_orders = [order for order in open_orders if order['isin'] == config.OPTION_TICKER]
        if ticker_orders:
            serial_numbers = [order['serialNumber'] for order in ticker_orders]
            api.cancel_orders(serial_numbers=serial_numbers)
        else:
            print(f"INFO: No open orders to cancel for ticker {config.OPTION_TICKER}.")
    else:
        print("INFO: No open orders found to cancel.")
