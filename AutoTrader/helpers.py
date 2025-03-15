# helpers.py

import numpy as np
import pandas as pd
import jdatetime
import datetime
from scipy.stats import norm
from collections import deque
from py_vollib.black_scholes import black_scholes
from py_vollib.black_scholes.implied_volatility import implied_volatility
from config import get_config
from py_vollib.black_scholes.greeks.analytical import delta

import math


def calculate_delta(avg_price_underlying, strike_price, time_to_expiration, risk_free_rate, estimated_vol, call_put):
    """
    Calculate the Delta of a European Call or Put option using the Black-Scholes Model.

    Args:
        avg_price_underlying (float): Current price of the underlying asset.
        strike_price (float): Strike price of the option.
        time_to_expiration (float): Time to expiration in years.
        risk_free_rate (float): Risk-free interest rate.
        estimated_vol (float): Estimated volatility.
        call_put (str): Option type ('c' for call, 'p' for put).

    Returns:
        float or None: Delta value or None if any input is None or not a valid number.
    """

    # Check if any input is None
    if (avg_price_underlying is None or strike_price is None or
            time_to_expiration is None or risk_free_rate is None or
            estimated_vol is None or call_put is None):
        return None

    # Check if any numeric input is NaN
    numeric_inputs = [avg_price_underlying, strike_price, time_to_expiration, risk_free_rate, estimated_vol]
    if any(isinstance(x, float) and math.isnan(x) for x in numeric_inputs):
        return None

    # Prevent potential division by zero errors in the Black-Scholes model
    if time_to_expiration <= 0 or estimated_vol <= 0:
        return 0

    # Assume delta is a predefined function for calculating the option's delta using Black-Scholes
    delta_value = delta(call_put, avg_price_underlying, strike_price, time_to_expiration, risk_free_rate, estimated_vol)
    return delta_value


def calculate_simple_moving_average(rolling_vols: deque) -> float:
    """
    Calculate the simple moving average (SMA) of implied volatility.

    Args:
        rolling_vols (deque): A deque of past implied volatilities.

    Returns:
        float: The SMA value.
    """
    if len(rolling_vols) > 0:
        return sum(rolling_vols) / len(rolling_vols)
    return np.nan


def calculate_estimated_volatility(implied_vol, rolling_vols):
    """
    Calculate the estimated volatility using SMA or EMA based on the smoothing_param.

    Args:
        implied_vol (float): The current implied volatility.
        rolling_vols (deque): A deque of past implied volatilities for SMA.

    Returns:
        Tuple[float, deque, float]: The estimated volatility, updated rolling_vols, and updated ema_estimated_vol.
    """

    estimated_vol = calculate_simple_moving_average(rolling_vols)
    if not pd.isnull(implied_vol):
        rolling_vols.append(implied_vol)

    return estimated_vol


def calculate_black_scholes_price(avg_price_underlying, strike_price, risk_free_rate, expiration_jalali_date, call_put,
                                  current_date_jalali, estimated_vol):
    """
    Calculate Black-Scholes price based on estimated volatility.

    Args:
        avg_price_underlying (float): Average price of the underlying asset.
        strike_price (float): Strike price of the option.
        risk_free_rate (float): Risk-free interest rate.
        expiration_jalali_date (str): Expiration date in Jalali calendar (YYYY-MM-DD).
        call_put (str): Option type ('c' for call, 'p' for put').
        current_date_jalali (str): Current date in Jalali calendar (YYYY-MM-DD).
        estimated_vol (float): Estimated volatility.

    Returns:
        float: The Black-Scholes price.
    """
    try:
        T = calculate_time_to_expiration(current_date_jalali, expiration_jalali_date)
        if T > 0 and estimated_vol > 0:
            return black_scholes(call_put, avg_price_underlying, strike_price, T, risk_free_rate, estimated_vol)
    except Exception as e:
        a = 2
    #    print(f"ERROR: Error calculating Black-Scholes price: {e}")
    return np.nan


def calculate_time_to_expiration(current_date: str, expiration_jalali_date: str) -> float:
    """
    Calculate the time to expiration (T) in years.

    Args:
        current_date (str): Current date in Jalali calendar (YYYY-MM-DD).
        expiration_jalali_date (str): Expiration date in Jalali calendar (YYYY-MM-DD).

    Returns:
        float: Time to expiration in years.
    """
    try:
        expiration_jalali = jdatetime.datetime.strptime(expiration_jalali_date, '%Y-%m-%d')
        expiration_gregorian = expiration_jalali.togregorian()

        current_jalali_date = jdatetime.datetime.strptime(current_date, '%Y-%m-%d')
        current_gregorian_date = current_jalali_date.togregorian()

        days_to_expiration = (expiration_gregorian - current_gregorian_date).days
        return days_to_expiration / 365  # Convert days to years
    except Exception as e:
        print(f"ERROR: Error calculating time to expiration: {e}")
    return 0.0


def calculate_implied_volatility(avg_price_option, avg_price_underlying, time_to_expiration, strike_price,
                                 risk_free_rate, call_put, counters):
    """
    Calculate implied volatility for the option.

    Args:
        avg_price_option (float): Average price of the option.
        avg_price_underlying (float): Average price of the underlying asset.
        time_to_expiration (float): Time to expiration in years.
        strike_price (float): Strike price of the option.
        risk_free_rate (float): Risk-free interest rate.
        call_put (str): Option type ('c' for call, 'p' for put').
        counters (ErrorCounters): An instance of the ErrorCounters class.

    Returns:
        float: The implied volatility.
    """
    try:
        iv = implied_volatility(
            avg_price_option,
            avg_price_underlying,
            strike_price,
            time_to_expiration,
            risk_free_rate,
            call_put
        )
        return iv
    except Exception as e:
        # print(f"ERROR: Error calculating implied volatility: {e}")
        counters.try_except_counter += 1
        return np.nan


def fetch_data(api, underlying_ticker, option_ticker):
    """
    Fetch data for the underlying and options market.

    Args:
        api (TradingAPI): An instance of the TradingAPI class.
        underlying_ticker (str): The ISIN ticker symbol for the underlying asset.
        option_ticker (str): The ISIN ticker symbol for the option.

    Returns:
        Tuple[Optional[List[float]], Optional[List[float]]]: Tuple containing underlying data and option data.
    """
    underlying_data = api.fetch_order_book(underlying_ticker)
    option_data = api.fetch_order_book(option_ticker)
    return underlying_data, option_data


def validate_time_and_data(current_time, underlying_data, option_data, counters):
    config = get_config()
    """
    Validate current time and market data for the underlying and options market.

    Args:
        current_time (datetime.time): The current time.
        underlying_data (Optional[List[float]]): Order book data for the underlying asset.
        option_data (Optional[List[float]]): Order book data for the option.
        counters (ErrorCounters): An instance of the ErrorCounters class.

    Returns:
        Tuple[Optional[float], Optional[float], bool]: Tuple containing average underlying price, average option price, and validation status.
    """
    # Check current time

    time = current_time
    if isinstance(time, str):
        current_time = datetime.datetime.strptime(time, "%H:%M:%S").time()
    elif isinstance(time, datetime.time):
        current_time = time
    else:
        print(type, time)
        print("ERROR IN HELPERS VALIDATE DATE TIME")

    if not (config.VALID_TIME_START <= current_time <= config.VALID_TIME_END):
        counters.skip_by_time_counter += 1
        return None, None, False

    # Validate data
    try:
        if not all([
            underlying_data, option_data,
            underlying_data[1], underlying_data[2],
            option_data[1], option_data[2],
            underlying_data[1] != 0, underlying_data[2] != 0,
            option_data[1] != 0, option_data[2] != 0
        ]):
            counters.null_counter += 1
            return None, None, False

        avg_price_underlying = (underlying_data[1] + underlying_data[2]) / 2
        avg_price_option = (option_data[1] + option_data[2]) / 2

        return avg_price_underlying, avg_price_option, True
    except Exception as e:
        print(f"ERROR: Error in validate_time_and_data: {e}")
        counters.try_except_counter += 1
        return None, None, False


def validate_time_and_data_preprocess(current_time, counters, avg_price_underlying, avg_price_option):
    """
    Validate current time and precomputed average prices for the underlying and options market.

    Args:
        current_time (datetime.time): The current time.
        counters (ErrorCounters): An instance of the ErrorCounters class.
        avg_price_underlying (float): Precomputed average price for the underlying asset.
        avg_price_option (float): Precomputed average price for the option.

    Returns:
        bool: Validation status.
    """
    config = get_config()
    # Check current time
    time = current_time
    if isinstance(time, str):
        current_time = datetime.datetime.strptime(time, "%H:%M:%S").time()
    elif isinstance(time, datetime.time):
        current_time = time
    else:
        print(type, time)
        print("ERROR IN HELPERS VALIDATE DATE TIME")
        return False

    if not (config.VALID_TIME_START <= current_time <= config.VALID_TIME_END):
        counters.skip_by_time_counter += 1
        return False

    # Validate the precomputed prices
    if avg_price_underlying is None or avg_price_option is None:
        counters.null_counter += 1
        return False

    if avg_price_underlying == 0 or avg_price_option == 0:
        counters.null_counter += 1
        return False

    return True


def update_signal(signal, delta, config):
    config.CURRENT_DELTA = delta
    trade_direction = config.TRADE_DIRECTION
    avg_delta_border = config.AVG_DELTA_BORDER
    call_put = config.CALL_PUT
    can_trade = config.CAN_TRADE_IN_SAME_DIRECTION
    net_worth = config.NET_WORTH
    delta_min = config.DELTA_MIN

    if trade_direction > avg_delta_border:
        if (call_put == 'c' and signal == "buy") or (call_put == 'p' and signal == "sell"):
            return "hold", can_trade, net_worth, trade_direction

    if trade_direction < -avg_delta_border:
        if (call_put == 'p' and signal == "buy") or (call_put == 'c' and signal == "sell"):
            return "hold", can_trade, net_worth, trade_direction

    if delta is None:
        return "hold", can_trade, net_worth, trade_direction

    if signal == "hold":
        return signal, can_trade, net_worth, trade_direction

    if not can_trade:
        if (signal == "buy" and net_worth >= 0) or (signal == "sell" and net_worth <= 0):
            return "hold", can_trade, net_worth, trade_direction
    else:
        if (signal == "buy" and net_worth >= 0) or (signal == "sell" and net_worth <= 0):
            if np.abs(delta) < delta_min:
                return "hold", can_trade, net_worth, trade_direction

    return signal, can_trade, net_worth, trade_direction
