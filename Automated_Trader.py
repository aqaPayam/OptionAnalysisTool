import json
import time
import logging
from typing import Optional, Tuple, List

import requests
import numpy as np
import pandas as pd
import jdatetime
from py_vollib.black_scholes import black_scholes
from py_vollib.black_scholes.implied_volatility import implied_volatility
from collections import deque
import os  # For environment variables

# ============================
# Configuration and Constants
# ============================

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API Endpoints
BASE_URL = 'https://api-bbi.ephoenix.ir/api/v2'
MARKET_URL = 'https://marketsheet1.ephoenix.ir/api'
MDAPI_URL = 'https://mdapi1.ephoenix.ir/api/v2'

# API Headers with Environment Variables for Security
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
    'Accept': 'application/json, text/plain, */*',
    'Cookie': os.getenv('API_COOKIE'),  # Set this environment variable securely
    'x-sessionId': os.getenv('API_SESSION_ID'),  # Set this environment variable securely
    'Content-Type': 'application/json'
}

# Trading Parameters
EXPIRATION_DATE = "1402-09-30"  # Example expiration date in Jalali (YYYY-MM-DD)
RISK_FREE_RATE = 0.05  # Example risk-free rate
STRIKE_PRICE = 100000  # Example strike price
CALL_PUT = 'call'  # Option type ('call' or 'put')

# Trading Session Time (Jalali Time)
VALID_TIME_START = pd.to_datetime("09:15:00").time()
VALID_TIME_END = pd.to_datetime("12:30:00").time()

# Retry and Sleep Configuration
MAX_RETRIES = 7
SLEEP_INTERVAL = 1  # seconds

# Volatility Smoothing Parameter
# - If float between 0 and 1: EMA with alpha = smoothing_param
# - If integer > 1: SMA with window size = smoothing_param
SMOOTHING_PARAM = 5  # Example: 5 for SMA, 0.3 for EMA

# Rolling Window Size for Signal Generation
WINDOW_SIZE = 20  # Number of past price differences to consider

# Z-score Threshold for Generating Signals
Z_THRESHOLD = 1.0  # Configurable threshold for generating buy/sell signals


# ====================
# Error Counter Class
# ====================

class ErrorCounters:
    """
    Class to keep track of various error and condition counters.
    """

    def __init__(self):
        self.null_counter = 0
        self.skip_by_time_counter = 0
        self.try_except_counter = 0
        self.key_error_counter = 0
        self.condition_error_counter = 0  # For condition-related errors

    def report(self):
        logger.info(f"Null data rows: {self.null_counter}")
        logger.info(f"Skipped rows by time: {self.skip_by_time_counter}")
        logger.info(f"Errors in implied volatility calculation: {self.try_except_counter}")
        logger.info(f"KeyErrors encountered: {self.key_error_counter}")
        logger.info(f"Condition-related errors: {self.condition_error_counter}")


# =====================
# Trading API Class
# =====================

class TradingAPI:
    """
    Class to interact with the trading API.
    """

    def __init__(self, max_retries: int = MAX_RETRIES):
        self.base_url = BASE_URL
        self.market_url = MARKET_URL
        self.mdapi_url = MDAPI_URL
        self.headers = HEADERS
        self.max_retries = max_retries

    def _make_request(self, method: str, url: str, data: Optional[dict] = None) -> Optional[dict]:
        """
        Makes an HTTP request with retries on failure.

        Args:
            method (str): HTTP method ('GET' or 'POST').
            url (str): The API endpoint URL.
            data (Optional[dict]): The payload for POST requests.

        Returns:
            Optional[dict]: The JSON response if successful, else None.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                if method.upper() == 'POST':
                    response = requests.post(url, headers=self.headers, data=json.dumps(data))
                elif method.upper() == 'GET':
                    response = requests.get(url, headers=self.headers)
                else:
                    logger.error(f"Unsupported HTTP method: {method}")
                    return None

                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt} failed for {url}: {e}")
                time.sleep(SLEEP_INTERVAL)
        logger.error(f"Max retries reached for {url}.")
        return None

    def fetch_order_book(self, ticker: str) -> Optional[List[float]]:
        """
        Retrieves the current order book for a specific ticker.

        Args:
            ticker (str): The ISIN ticker symbol.

        Returns:
            Optional[List[float]]: A list containing [sell_volume, sell_price, buy_price, buy_volume].
        """
        url = f"{self.market_url}/Queue/BestLimitWithSize?isin={ticker}"
        response = self._make_request('GET', url)
        if response:
            try:
                buy = response['buy'][0]
                sell = response['sell'][0]
                return [sell['v'], sell['p'], buy['p'], buy['v']]
            except (KeyError, IndexError) as e:
                logger.error(f"Error extracting order book data for {ticker}: {e}")
        return None

    def place_order(self, ticker: str, price: float, quantity: int, side: str) -> Optional[dict]:
        """
        Sends a new order to the trading API.

        Args:
            ticker (str): The ISIN ticker symbol.
            price (float): The price at which to place the order.
            quantity (int): The volume of the order.
            side (str): 'buy' or 'sell'.

        Returns:
            Optional[dict]: The API response if successful, else None.
        """
        url = f"{self.base_url}/orders/NewOrder"
        data = {
            "validity": 1,
            "validityDate": None,
            "price": price,
            "volume": quantity,
            "side": 1 if side.lower() == 'buy' else 2,
            "isin": ticker,
            "accountType": 1
        }
        return self._make_request('POST', url, data)

    def modify_order(self, price: float, order_id: int, volume: int, ticker: str) -> Optional[dict]:
        """
        Edits an existing order.

        Args:
            price (float): The new price for the order.
            order_id (int): The serial number of the order to modify.
            volume (int): The new volume for the order.
            ticker (str): The ISIN ticker symbol.

        Returns:
            Optional[dict]: The API response if successful, else None.
        """
        url = f"{self.base_url}/orders/EditOrder"
        data = {
            "validity": 1,
            "validityDate": None,
            "price": price,
            "volume": volume,
            "side": 1,  # Assuming 'buy' side; adjust as needed
            "isin": ticker,
            "accountType": 1,
            "serialNumber": order_id
        }
        return self._make_request('POST', url, data)

    def fetch_open_orders(self) -> Optional[List[dict]]:
        """
        Retrieves all open orders.

        Returns:
            Optional[List[dict]]: A list of open orders if successful, else None.
        """
        url = f"{self.base_url}/orders/GetOpenOrders"
        return self._make_request('GET', url)

    def manage_sell_orders(self, ticker: str, price: float, quantity: int) -> None:
        """
        Manages sell orders for a specific ticker.

        Args:
            ticker (str): The ISIN ticker symbol.
            price (float): The price at which to place the sell order.
            quantity (int): The volume of the sell order.
        """
        response = self.fetch_open_orders()
        if not response:
            self.place_order(ticker, price, quantity, 'sell')
            return

        sell_orders = [order for order in response if int(order.get('orderSide', 0)) == 2]
        if not sell_orders:
            self.place_order(ticker, price, quantity, 'sell')
            return

        for order in sell_orders:
            if ticker == order.get('isin'):
                current_price = int(order.get('price', 0))
                if price in {current_price, current_price - 10}:
                    return
                self.modify_order(price, int(order.get('serialNumber', 0)), quantity, ticker)
                return
        self.place_order(ticker, price, quantity, 'sell')

    def fetch_remaining_quota(self) -> Optional[int]:
        """
        Retrieves the remaining trading quota.

        Returns:
            Optional[int]: The remaining quota if successful, else None.
        """
        url = f"{self.base_url}/tradingbook/GetLastTradingBook"
        response = self._make_request('GET', url)
        return response.get('remain') if response else None

    def fetch_ticker_data(self, ticker: str) -> Optional[dict]:
        """
        Fetches current market data for a specific ticker.

        Args:
            ticker (str): The ISIN ticker symbol.

        Returns:
            Optional[dict]: The market data if successful, else None.
        """
        url = f"{self.mdapi_url}/instruments/full"
        data = {"isinList": [ticker]}
        return self._make_request('POST', url, data)

    def fetch_trades(self) -> List[dict]:
        """
        Retrieves a list of trades executed today.

        Returns:
            List[dict]: A list of trade dictionaries.
        """
        url = f"{self.base_url}/Trades/GetDayTrades"
        response = self._make_request('GET', url)
        trades = []
        if response:
            for trade in response:
                if trade.get('tradeType') != 2:
                    trades.append({
                        "ticker": trade.get('isin'),
                        "execute": trade.get('volume'),
                        "orderside": 'buy' if trade.get('tradeType') == 1 else 'sell',
                        "value": trade.get('netAmount'),
                        "price": trade.get('avgPrice')
                    })
        return trades


# =============================
# Placeholder for Buy/Sell Actions
# =============================

def buy():
    """
    Implement your buy logic here.
    """
    logger.info("Executing Buy Order")
    # TODO: Add actual buy order execution code here


def sell():
    """
    Implement your sell logic here.
    """
    logger.info("Executing Sell Order")
    # TODO: Add actual sell order execution code here


# ============================
# Helper Functions
# ============================

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


def calculate_estimated_volatility(
        implied_vol: float,
        rolling_vols: deque,
        ema_estimated_vol: float,
        smoothing_param: float
) -> Tuple[float, float]:
    """
    Calculate the estimated volatility using SMA or EMA based on the smoothing_param.

    Args:
        implied_vol (float): The current implied volatility.
        rolling_vols (deque): A deque of past implied volatilities for SMA.
        ema_estimated_vol (float): The current EMA value.
        smoothing_param (float): The smoothing parameter (alpha for EMA or window size for SMA).

    Returns:
        Tuple[float, float]: The estimated volatility and the updated EMA value.
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
    return estimated_vol, ema_estimated_vol


def calculate_black_scholes_price(
        avg_price_underlying: float,
        strike_price: float,
        risk_free_rate: float,
        expiration_jalali_date: str,
        call_put: str,
        current_date_jalali: str,
        estimated_vol: float
) -> float:
    """
    Calculate Black-Scholes price based on estimated volatility.

    Args:
        avg_price_underlying (float): Average price of the underlying asset.
        strike_price (float): Strike price of the option.
        risk_free_rate (float): Risk-free interest rate.
        expiration_jalali_date (str): Expiration date in Jalali calendar (YYYY-MM-DD).
        call_put (str): Option type ('call' or 'put').
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
        logger.error(f"Error calculating Black-Scholes price: {e}")
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
        logger.error(f"Error calculating time to expiration: {e}")
    return 0.0


def fetch_data(api: TradingAPI, underlying_ticker: str, option_ticker: str) -> Tuple[
    Optional[List[float]], Optional[List[float]]]:
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


def validate_time_and_data(
        current_time: pd.Timestamp.time,
        underlying_data: Optional[List[float]],
        option_data: Optional[List[float]],
        counters: ErrorCounters
) -> Tuple[Optional[float], Optional[float], bool]:
    """
    Validate current time and market data for the underlying and options market.

    Args:
        current_time (pd.Timestamp.time): The current time.
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


def calculate_implied_volatility(
        avg_price_option: float,
        avg_price_underlying: float,
        time_to_expiration: float,
        strike_price: float,
        risk_free_rate: float,
        call_put: str,
        counters: ErrorCounters
) -> float:
    """
    Calculate implied volatility for the option.

    Args:
        avg_price_option (float): Average price of the option.
        avg_price_underlying (float): Average price of the underlying asset.
        time_to_expiration (float): Time to expiration in years.
        strike_price (float): Strike price of the option.
        risk_free_rate (float): Risk-free interest rate.
        call_put (str): Option type ('call' or 'put').
        counters (ErrorCounters): An instance of the ErrorCounters class.

    Returns:
        float: The implied volatility.
    """
    try:
        iv = implied_volatility(avg_price_option, avg_price_underlying, strike_price, time_to_expiration,
                                risk_free_rate, call_put)
        return iv
    except Exception as e:
        logger.error(f"Error calculating implied volatility: {e}")
        counters.try_except_counter += 1
        return np.nan


# ================================
# Signal Generation and Processing
# ================================

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


def process_price_difference(
        price_difference: float,
        price_diff_window: deque,
        window_size: int,
        z_threshold: float,
        counters: ErrorCounters
) -> Tuple[str, float, float, float, float, float]:
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
        if len(price_diff_window) >= window_size and not any(pd.isnull(price_diff_window)):
            rolling_mean_diff = np.mean(price_diff_window)
            rolling_std_diff = np.std(price_diff_window, ddof=1)
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

        # Execute signals
        if signal == 'buy':
            buy()
        elif signal == 'sell':
            sell()

        # Append the new price_difference to the window AFTER signal generation
        if not pd.isnull(price_difference):
            price_diff_window.append(price_difference)
        else:
            price_diff_window.append(np.nan)

        return signal, under_count, over_count, rolling_mean_diff, rolling_std_diff, z_score

    except Exception as e:
        logger.exception(f"Error in processing price difference: {e}")
        counters.try_except_counter += 1
        return 'hold', 0, 0, np.nan, np.nan, np.nan


# ============================
# Main Execution Function
# ============================

def main():
    """
    Main function to execute the trading strategy.
    """
    # Initialize API and error counters
    api = TradingAPI()
    counters = ErrorCounters()

    # Initialize DataFrame to store trading data
    columns = [
        "Date", "Time", "avg_price_underlying", "avg_price_option",
        "black_scholes_price", "implied_vol", "estimated_vol",
        "price_difference", "rolling_mean_diff", "rolling_std_diff", "z_score"
    ]
    data = pd.DataFrame(columns=columns)

    # Define your tickers (Replace with actual ISIN tickers)
    UNDERLYING_TICKER = "UNDERLYING_ISIN"  # Replace with actual ticker
    OPTION_TICKER = "OPTION_ISIN"  # Replace with actual ticker

    # Initialize variables for volatility calculation
    rolling_vols = deque(maxlen=SMOOTHING_PARAM if SMOOTHING_PARAM > 1 else None)
    ema_estimated_vol = np.nan  # Initial EMA value

    # Initialize deque for rolling price differences
    price_diff_window = deque(maxlen=WINDOW_SIZE)

    # Initialize counters for z_score
    under_negative_one_count = 0
    over_positive_one_count = 0

    try:
        while True:
            try:
                # Get current Jalali date and time
                now = jdatetime.datetime.now()
                current_date_jalali = now.strftime('%Y-%m-%d')
                current_time = now.time()

                # Fetch data
                underlying_data, option_data = fetch_data(api, UNDERLYING_TICKER, OPTION_TICKER)

                # Validate data and time
                avg_price_underlying, avg_price_option, is_valid = validate_time_and_data(
                    current_time, underlying_data, option_data, counters
                )

                if not is_valid:
                    logger.info("Skipping due to invalid time or data.")
                    time.sleep(SLEEP_INTERVAL)
                    continue

                # Calculate time to expiration
                time_to_expiration = calculate_time_to_expiration(current_date_jalali, EXPIRATION_DATE)
                if time_to_expiration <= 0:
                    logger.warning("Expiration date reached or passed.")
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
                    avg_price_underlying=avg_price_underlying,
                    strike_price=STRIKE_PRICE,
                    risk_free_rate=RISK_FREE_RATE,
                    expiration_jalali_date=EXPIRATION_DATE,
                    call_put=CALL_PUT,
                    current_date_jalali=current_date_jalali,
                    estimated_vol=estimated_vol
                )

                # Calculate price difference
                price_difference = avg_price_option - black_scholes_price

                # Process price difference and generate signals
                signal, under_count, over_count, rolling_mean_diff, rolling_std_diff, z_score = process_price_difference(
                    price_difference, price_diff_window, WINDOW_SIZE, Z_THRESHOLD, counters
                )

                # Update z-score counts
                under_negative_one_count += under_count
                over_positive_one_count += over_count

                # Append data to DataFrame
                new_row = {
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
                    "z_score": z_score
                }
                data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

                # Log the results
                logger.info(f"Underlying Avg Price: {avg_price_underlying}")
                logger.info(f"Option Avg Price: {avg_price_option}")
                logger.info(f"Implied Volatility: {implied_vol}")
                logger.info(f"Estimated Volatility: {estimated_vol}")
                logger.info(f"Black-Scholes Price: {black_scholes_price}")
                logger.info(f"Price Difference: {price_difference}")
                logger.info(f"Rolling Mean Difference: {rolling_mean_diff}")
                logger.info(f"Rolling Std Dev Difference: {rolling_std_diff}")
                logger.info(f"Z-Score: {z_score}")
                logger.info(f"Z-Score < -{Z_THRESHOLD} Count: {under_negative_one_count}")
                logger.info(f"Z-Score > +{Z_THRESHOLD} Count: {over_positive_one_count}")

                time.sleep(SLEEP_INTERVAL)
            except KeyError as e:
                counters.key_error_counter += 1
                logger.error(f"KeyError encountered: {e}")
            except ValueError as e:
                counters.condition_error_counter += 1
                logger.error(f"Condition error: {e}")
            except Exception as e:
                counters.try_except_counter += 1
                logger.exception(f"Unexpected error: {e}")
    except KeyboardInterrupt:
        logger.info("Processing stopped by user.")
    finally:
        # Report error counters
        counters.report()
        # Optionally, save DataFrame to a file upon termination
        # data.to_csv("trading_data.csv", index=False)
        logger.info("Program terminated.")


# ===================
# Entry Point
# ===================

if __name__ == "__main__":
    main()
