# data_fetching.py

import time
import jdatetime
from helpers import fetch_data
from config import SLEEP_INTERVAL
from config import UNDERLYING_TICKER
from config import OPTION_TICKER

def data_fetching_thread(api, data_queue, counters):
    """
    Thread function for data fetching.
    """
    while True:
        try:
            now = jdatetime.datetime.now()

            # Separating date and time
            current_date = now.strftime("%Y-%m-%d")  # Format for date string
            current_time = now.strftime("%H:%M:%S")  # Format for time  string

            # Fetch data
            underlying_data, option_data = fetch_data(api, UNDERLYING_TICKER, OPTION_TICKER)
            if underlying_data is None and  option_data is None:
                print("fetched data is null")
            else:
            # Put data into the queue
                data_queue.append((current_date, current_time, underlying_data, option_data))
                
            time.sleep(SLEEP_INTERVAL)
        except Exception as e:
            counters.try_except_counter += 1
            print(f"ERROR: Exception in data_fetching_thread: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(SLEEP_INTERVAL)
