# data_fetching.py

import time
import jdatetime
from helpers import fetch_data

def data_fetching_thread(api, data_queue, counters):
    """
    Thread function for data fetching.
    """
    while True:
        try:
            now = jdatetime.datetime.now()
            current_time = now.time()

            # Fetch data
            underlying_data, option_data = fetch_data(api, api, counters)

            # Put data into the queue
            data_queue.append((now, current_time, underlying_data, option_data))
            time.sleep(SLEEP_INTERVAL)
        except Exception as e:
            counters.try_except_counter += 1
            print(f"ERROR: Exception in data_fetching_thread: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(SLEEP_INTERVAL)
