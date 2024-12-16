import time
from signals import buy, sell, cancel_all_orders


def signal_handling_thread(signal_queue, stop_event):
    """
    Thread function for handling signals.
    """
    last_signal = None
    try:
        while not stop_event.is_set():
            time.sleep(0.01)
            if signal_queue:
                signal_data = signal_queue.popleft()
                current_time = signal_data.get("Time")
                signal = signal_data.get("signal")

                if signal == 'buy':
                    buy()
                elif signal == 'sell':
                    sell()
                elif signal == 'hold' and last_signal != 'hold':
                    cancel_all_orders()
                last_signal = signal
    finally:
        print("INFO: signal_handling_thread is shutting down gracefully.")
