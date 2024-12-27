import time

import pandas as pd
import jdatetime

CURRENT_MODE = None


class BaseConfig:
    # Shared settings across all modes
    BASE_URL = 'https://api-bbi.ephoenix.ir/api/v2'
    MARKET_URL = 'https://marketsheet1.ephoenix.ir/api'
    MDAPI_URL = 'https://mdapi1.ephoenix.ir/api/v2'

    HEADERS = {
        'User-Agent': '',
        # Empty User-Agent
        'Accept': 'application/json, text/plain, */*',
        'Cookie': '',
        # Empty Cookie
        'x-sessionId': '',  # Empty x-sessionId
        'Content-Type': 'application/json',
    }

    RISK_FREE_RATE = 0.3
    USE_HISTORICAL = True
    CALL_PUT = 'c'  # 'c' for call, 'p' for put
    VALID_TIME_START = pd.to_datetime("09:15:00").time()
    VALID_TIME_END = pd.to_datetime("12:30:00").time()
    MAX_RETRIES = 7
    SLEEP_INTERVAL = 1  # seconds
    MAX_SIZE = 10
    SMOOTHING_PARAM = 3600
    WINDOW_SIZE = 3600
    Z_THRESHOLD = 1.5
    BUY_PRICE_OFFSET = -1
    SELL_PRICE_OFFSET = 1
    ORDER_PRICE = 1000000 / 100

    HISTORICAL_DATA_START_DATE = (jdatetime.date.today() - jdatetime.timedelta(days=4)).strftime('%Y-%m-%d')
    HISTORICAL_DATA_END_DATE = jdatetime.date.today().strftime('%Y-%m-%d')


class AhromConfig(BaseConfig):
    UNDERLYING_NAME = "اهرم"
    UNDERLYING_TICKER = "IRT1AHRM0001"
    OPTION_NAME = "ضهرم1007"
    OPTION_TICKER = "IRO9AHRM2401"
    EXPIRATION_DATE = "1403-10-26"
    STRIKE_PRICE = 18000


class KhodroConfig(BaseConfig):
    UNDERLYING_NAME = "خودرو"
    UNDERLYING_TICKER = "IRO1IKCO0001"
    OPTION_NAME = "ضخود1136"
    OPTION_TICKER = "IRO9IKCO8K51"
    EXPIRATION_DATE = "1403-11-03"
    STRIKE_PRICE = 3000


class ShastaConfig(BaseConfig):
    UNDERLYING_NAME = "شستا"
    UNDERLYING_TICKER = "IRO1TAMN0001"
    OPTION_NAME = "ضستا1125"
    OPTION_TICKER = "IRO9TAMN0411"
    EXPIRATION_DATE = "1403-11-10"
    STRIKE_PRICE = 1050


# Map modes to configurations
CONFIGS = {
    'ahrom': AhromConfig,
    'khodro': KhodroConfig,
    'shasta': ShastaConfig,
}


def set_current_mode(mode):
    """
    Sets the current mode globally.
    """
    global CURRENT_MODE
    if mode not in CONFIGS:
        raise ValueError(f"Invalid mode: {mode}")
    CURRENT_MODE = mode


def get_config():
    """
    Waits for the current mode to be set and then retrieves the configuration.
    """
    global CURRENT_MODE
    while CURRENT_MODE is None:
        time.sleep(0.01)  # Wait a short time to avoid busy waiting
    return CONFIGS[CURRENT_MODE]
