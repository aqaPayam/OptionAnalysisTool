import time
import jdatetime
from helpers import fetch_data
from config import get_config

config = get_config()


def data_fetching_thread(api, data_queue, counters, stop_event):
    """
    Thread function for data fetching.
    """
    try:
        while not stop_event.is_set():
            start_time = time.time()
            now = jdatetime.datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")

            underlying_data, option_data = fetch_data(api, config.UNDERLYING_TICKER, config.OPTION_TICKER)
            if underlying_data is None and option_data is None:
                print("Fetched data is null")
            else:
                data_queue.append((current_date, current_time, underlying_data, option_data))

            elapsed_time = time.time() - start_time
            sleep_time = max(0, config.SLEEP_INTERVAL - elapsed_time)
            time.sleep(sleep_time)
    except Exception as e:
        counters.try_except_counter += 1
        print(f"ERROR: Exception in data_fetching_thread: {e}")
        import traceback
        traceback.print_exc()
        # If exception occurs, the thread ends here and finally will execute
    finally:
        print("INFO: data_fetching_thread is shutting down gracefully.")
