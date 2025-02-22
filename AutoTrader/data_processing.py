import time
import jdatetime
import numpy as np
from helpers import (
    validate_time_and_data, calculate_time_to_expiration,
    calculate_implied_volatility, calculate_estimated_volatility,
    calculate_black_scholes_price, calculate_delta, update_signal  # Added Delta import
)
from signals import process_price_difference
from config import get_config


def processing_thread(data_queue, result_queue, signal_queue, counters, processing_ready_event, rolling_vols,
                      price_diff_window, stop_event):
    """
    Thread function for data processing and signal generation.
    """
    global implied_vol
    config = get_config()

    print("INFO: Processing thread waiting for historical data to be ready...")
    processing_ready_event.wait()
    print("INFO: Historical data is ready. Processing thread starting analysis.")

    under_negative_one_count = 0
    over_positive_one_count = 0

    try:
        while not stop_event.is_set():
            time.sleep(0.01)
            if data_queue:
                current_date_jalali, current_time, underlying_data, option_data = data_queue.popleft()

                avg_price_underlying, avg_price_option, is_valid = validate_time_and_data(
                    current_time, underlying_data, option_data, counters
                )
                if not is_valid:
                    print("INFO: Skipping due to invalid data or time :data has 0 :")
                    continue

                time_to_expiration = calculate_time_to_expiration(current_date_jalali, config.EXPIRATION_DATE)
                if time_to_expiration <= 0:
                    print("WARNING: Expiration date reached or passed.")
                    break

                implied_vol = calculate_implied_volatility(
                    avg_price_option, avg_price_underlying, time_to_expiration, config.STRIKE_PRICE,
                    config.RISK_FREE_RATE, config.CALL_PUT, counters
                )

                estimated_vol = calculate_estimated_volatility(
                    implied_vol, rolling_vols
                )

                black_scholes_price = calculate_black_scholes_price(
                    avg_price_underlying, config.STRIKE_PRICE, config.RISK_FREE_RATE,
                    config.EXPIRATION_DATE, config.CALL_PUT, current_date_jalali, estimated_vol
                )

                price_difference = avg_price_option - black_scholes_price

                # **Delta Calculation**
                delta = calculate_delta(
                    avg_price_underlying, config.STRIKE_PRICE, time_to_expiration,
                    config.RISK_FREE_RATE, estimated_vol, config.CALL_PUT
                )

                signal, under_count, over_count, rolling_mean_diff, rolling_std_diff, z_score = process_price_difference(
                    price_difference, price_diff_window, config.WINDOW_SIZE, config.Z_THRESHOLD, counters
                )

                under_negative_one_count += under_count
                over_positive_one_count += over_count

                signal = update_signal(signal, delta, config)

                result = {
                    "Date": current_date_jalali,
                    "Time": current_time,
                    "avg_price_underlying": avg_price_underlying,
                    "avg_price_option": avg_price_option,
                    "black_scholes_price": black_scholes_price,
                    "implied_vol": implied_vol,
                    "estimated_vol": estimated_vol,
                    "price_difference": price_difference,
                    "rolling_mean_diff": rolling_mean_diff,
                    "rolling_std_diff": rolling_std_diff,
                    "z_score": z_score,
                    "signal": signal,  # Updated signal if necessary
                    "delta": delta,  # Added Delta to results
                    "under_negative_one_count": under_negative_one_count,
                    "over_positive_one_count": over_positive_one_count,
                }

                result_queue.append(result)
                signal_queue.append({"Time": current_time, "signal": signal})
    finally:
        print("INFO: processing_thread is shutting down gracefully.")
