# helpers.py

import numpy as np
import pandas as pd
import jdatetime
from collections import deque
from py_vollib.black_scholes import black_scholes
from py_vollib.black_scholes.implied_volatility import implied_volatility
from config import SMOOTHING_PARAM, CALL_PUT, RISK_FREE_RATE, STRIKE_PRICE, VALID_TIME_START, VALID_TIME_END

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

def calculate_exponential_moving_average(previous_ema: float, implied_vol: float, alpha: float) -> float:
    """
    Update the exponential moving average (EMA) of implied volatility.

    Args:
        previous_ema (float): The previous EMA value.
        implied_vol (float): The current implied volatility.
        alpha (float): The smoothing factor for EMA.

    Returns:
        float: The updated EMA value.
    """
    if np.isnan(previous_ema) and not pd.isnull(implied_vol):
        return implied_vol
    elif not pd.isnull(implied_vol):
        return alpha * implied_vol + (1 - alpha) * previous_ema
    return previous_ema

def calculate_estimated_volatility(implied_vol, rolling_vols, ema_estimated_vol, smoothing_param):
    """
    Calculate the estimated volatility using SMA or EMA based on the smoothing_param.

    Args:
        implied_vol (float): The current implied volatility.
        rolling_vols (deque): A deque of past implied volatilities for SMA.
        ema_estimated_vol (float): The current EMA value.
        smoothing_param (float): The smoothing parameter (alpha for EMA or window size for SMA).

    Returns:
        Tuple[float, deque, float]: The estimated volatility, updated rolling_vols, and updated ema_estimated_vol.
    """
    if 0 < smoothing_param <= 1:
        # EMA Mode
        estimated_vol = ema_estimated_vol
        ema_estimated_vol = calculate_exponential_moving_average(ema_estimated_vol, implied_vol, smoothing_param)
    elif smoothing_param > 1:
        # SMA Mode
        estimated_vol = calculate_simple_moving_average(rolling_vols)
        if not pd.isnull(implied_vol):
            rolling_vols.append(implied_vol)
    else:
        raise ValueError(
            "smoothing_param must be a float (0 < smoothing_param <= 1) for EMA or an integer > 1 for SMA.")
    return estimated_vol, rolling_vols, ema_estimated_vol

def calculate_black_scholes_price(avg_price_underlying, strike_price, risk_free_rate, expiration_jalali_date, call_put, current_date_jalali, estimated_vol):
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
        print(f"ERROR: Error calculating Black-Scholes price: {e}")
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

def calculate_implied_volatility(avg_price_option, avg_price_underlying, time_to_expiration, strike_price, risk_free_rate, call_put, counters):
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
        print(f"ERROR: Error calculating implied volatility: {e}")
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
    if not (VALID_TIME_START <= current_time <= VALID_TIME_END):
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
