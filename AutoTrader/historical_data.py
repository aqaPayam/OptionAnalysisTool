# historical_data.py

import traceback

from data_preprocessing import process_and_flatten_market_data  # Updated import
from config import (
    UNDERLYING_NAME, OPTION_NAME, HISTORICAL_DATA_START_DATE,
    HISTORICAL_DATA_END_DATE, STRIKE_PRICE, RISK_FREE_RATE,
    EXPIRATION_DATE, CALL_PUT, SAVE_FOLDER, JUST_DOWNLOAD
)


def historical_data_thread(historical_data_ready_event, historical_data_container):
    """
    Thread function for downloading and processing historical data.
    """
    print("INFO: Historical data thread started.")
    try:
        # Run the data processing function to get historical data
        historical_data = process_and_flatten_market_data(
            underlying_stock=UNDERLYING_NAME,
            option_stock=OPTION_NAME,
            start_date=HISTORICAL_DATA_START_DATE,
            end_date=HISTORICAL_DATA_END_DATE,
            strike_price=STRIKE_PRICE,
            risk_free_rate=RISK_FREE_RATE,
            expiration_jalali_date=EXPIRATION_DATE,
            call_put=CALL_PUT,
            save_folder=SAVE_FOLDER,
            just_download=JUST_DOWNLOAD
        )

        # Store the historical data in the shared container
        historical_data_container['data'] = historical_data

        print("INFO: Historical data is ready.")
    except Exception as e:
        print(f"ERROR: Exception in historical_data_thread: {e}")
        traceback.print_exc()
    finally:
        # Signal that historical data is ready
        historical_data_ready_event.set()
