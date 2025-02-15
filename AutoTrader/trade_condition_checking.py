import threading
import time
from datetime import datetime
from jdatetime import date as jdate  # For Jalali date conversion
from config import get_config


def run_trade_checker(api, stop_event):
    """
    Checks expiration date and total traded volume at intervals.
    If expiration is valid and volume meets the threshold, enables trading (`CAN_TRADE_AGAINST_MARKET = True`) and exits.
    Otherwise, it keeps checking periodically.

    Args:
        api (TradingAPI): An instance of TradingAPI to fetch total traded volume.
        stop_event (threading.Event): A shared event to stop the thread externally.
    """
    config = get_config()  # Load config values

    # Get today's Jalali date
    today_gregorian = datetime.today().date()
    today_jalali = jdate.fromgregorian(date=today_gregorian)

    # Convert expiration date from config to Jalali object
    expiration_jalali = jdate(*map(int, config.EXPIRATION_DATE.split('-')))

    # Calculate remaining days
    remaining_days = (expiration_jalali - today_jalali).days

    # Expiration date check: If it's too close, disable trading and stop the thread
    if remaining_days < config.MIN_REMAINING_DAYS:
        print(f"ERROR: Expiration date limit reached! ({remaining_days} days left)")
        config.CAN_TRADE_IN_SAME_DIRECTION = False  # Ensure trading stays disabled
        return  # Exit the thread (but NOT the entire program)

    while not stop_event.is_set():  # Keep running unless stopped externally

        # Fetch total traded volume
        total_volume = api.fetch_total_traded_volume()

        # Check if volume meets the required threshold
        if total_volume is not None and total_volume >= config.MIN_VOLUME_LIMIT:
            print(f"INFO: Trading enabled! Volume: {total_volume}, Days remaining: {remaining_days}")

            # Enable trading
            config.CAN_TRADE_IN_SAME_DIRECTION = True

            # Exit the thread since conditions are met
            return
        else:
            print(f"WARNING: Volume too low ({total_volume}), retrying in {config.CONDITION_CHECK_INTERVAL} seconds...")

        # Wait before checking again
        time.sleep(config.CONDITION_CHECK_INTERVAL)
