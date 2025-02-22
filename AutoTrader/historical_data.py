import traceback
from data_preprocessing import process_and_flatten_market_data
from config import get_config


def historical_data_thread(historical_data_ready_event, historical_data_container, stop_event):
    config = get_config()
    """
    Thread function for downloading and processing historical data.
    """
    print("INFO: Historical data thread started.")
    try:
        if stop_event.is_set():
            return
        historical_data = process_and_flatten_market_data(
            underlying_stock=config.UNDERLYING_NAME,
            option_stock=config.OPTION_NAME,
            start_date=config.HISTORICAL_DATA_START_DATE,
            end_date=config.HISTORICAL_DATA_END_DATE,
            strike_price=config.STRIKE_PRICE,
            risk_free_rate=config.RISK_FREE_RATE,
            expiration_jalali_date=config.EXPIRATION_DATE,
            call_put=config.CALL_PUT,
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
