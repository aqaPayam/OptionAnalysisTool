# net_worth_monitor.py

import time
from threading import Event

from trading_api import TradingAPI
from config import get_config


def monitor_net_worth(stop_event: Event) -> None:
    """
    Monitors the net worth balance every 5 seconds and updates config.NET_WORTH.

    This function is intended to be run in a separate thread. It continuously
    creates an instance of TradingAPI and calls get_net_worth_balance at the
    specified interval until the stop_event is set.

    Args:
        stop_event (Event): An event to signal the thread to stop gracefully.
    """
    # Initialize the TradingAPI instance
    api = TradingAPI()
    # Retrieve the configuration instance
    config = get_config()

    print("[Net Worth Monitor] Started monitoring net worth balance.")

    while not stop_event.is_set():
        try:
            # Fetch the current net worth balance
            net_worth, vol = api.get_net_worth_balance()
            # manfi bashe foroosh mosbat bashe kharid

            if net_worth is not None:
                # Update the NET_WORTH in the configuration
                config.NET_WORTH = net_worth
                config.VOLUME = vol
                print(f"[Net Worth Monitor] NET_WORTH updated to: {net_worth}")
            else:
                print("[Net Worth Monitor] Warning: NET_WORTH is None.")

        except Exception as e:
            print(f"[Net Worth Monitor] ERROR: Failed to fetch net worth balance: {e}")

        # Wait for 5 seconds or until stop_event is set
        # This allows the thread to exit promptly if stop_event is triggered
        if stop_event.wait(1):
            break

    print("[Net Worth Monitor] Stopped monitoring net worth balance.")
