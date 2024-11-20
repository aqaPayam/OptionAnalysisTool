# data_processing.py

import time
import jdatetime
import numpy as np
from helpers import (
    validate_time_and_data, calculate_time_to_expiration,
    calculate_implied_volatility, calculate_estimated_volatility,
    calculate_black_scholes_price
)
from signals import process_price_difference, buy, sell, cancel_all_orders
from config import (
    EXPIRATION_DATE, STRIKE_PRICE, RISK_FREE_RATE, CALL_PUT,
    SLEEP_INTERVAL, Z_THRESHOLD
)

def processing_thread(data_queue, result_queue, counters, processing_ready_event, rolling_vols, price_diff_window):
    """
    Thread function for data processing and signal generation.
    """
    # Wait until the historical data is ready
    print("INFO: Processing thread waiting for historical data to be ready...")
    processing_ready_event.wait()
    print("INFO: Historical data is ready. Processing thread starting analysis.")

    # Initialize variables
    ema_estimated_vol = np.nan  # Initial EMA value
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
