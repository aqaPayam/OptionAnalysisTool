# signal_handling.py

import time
from signals import buy, sell, cancel_all_orders


def signal_handling_thread(signal_queue):
    """
    Thread function for handling signals and executing trading actions.
    Avoids redundant actions if the previous signal was also 'hold'.
    """
    last_signal = None

    while True:
        if signal_queue:
            signal_data = signal_queue.popleft()
            current_time = signal_data.get("Time")
            signal = signal_data.get("signal")

            # Execute trading actions based on the signal
            # Only cancel orders on 'hold' if the previous signal wasn't also 'hold'
            if signal == 'buy':
                buy()
            elif signal == 'sell':
                sell()
            elif signal == 'hold' and last_signal != 'hold':
                cancel_all_orders()

            # Update the last signal
            last_signal = signal
