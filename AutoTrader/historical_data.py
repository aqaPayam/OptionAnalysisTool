import traceback
from data_preprocessing import process_and_flatten_market_data
from config import (
    UNDERLYING_NAME, OPTION_NAME, HISTORICAL_DATA_START_DATE,
    HISTORICAL_DATA_END_DATE, STRIKE_PRICE, RISK_FREE_RATE,
    EXPIRATION_DATE, CALL_PUT
)


def historical_data_thread(historical_data_ready_event, historical_data_container, stop_event):
    """
    Thread function for downloading and processing historical data.
    """
    print("INFO: Historical data thread started.")
    try:
        if stop_event.is_set():
            return
        historical_data = process_and_flatten_market_data(
            underlying_stock=UNDERLYING_NAME,
            option_stock=OPTION_NAME,
            start_date=HISTORICAL_DATA_START_DATE,
            end_date=HISTORICAL_DATA_END_DATE,
            strike_price=STRIKE_PRICE,
            risk_free_rate=RISK_FREE_RATE,
            expiration_jalali_date=EXPIRATION_DATE,
            call_put=CALL_PUT,
            save_folder="data_files",
            just_download=False
        )
        historical_data_container['data'] = historical_data
        print("INFO: Historical data is ready.")
    except Exception as e:
        print(f"ERROR: Exception in historical_data_thread: {e}")
        traceback.print_exc()
    finally:
        historical_data_ready_event.set()
        print("INFO: historical_data_thread is shutting down gracefully.")
