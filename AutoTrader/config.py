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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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
    MAX_RETRIES = 3
    SLEEP_INTERVAL = 1  # seconds
    MAX_SIZE = 10
    SMOOTHING_PARAM = 3600
    WINDOW_SIZE = 3600
    Z_THRESHOLD = 1.5
    BUY_PRICE_OFFSET = 0
    SELL_PRICE_OFFSET = 0
    ORDER_PRICE = 1000000 // 100
    MAX_BID = 25000000 * 10
    NET_WORTH = 0

    HISTORICAL_DATA_START_DATE = (jdatetime.date.today() - jdatetime.timedelta(days=4)).strftime('%Y-%m-%d')
    HISTORICAL_DATA_END_DATE = jdatetime.date.today().strftime('%Y-%m-%d')


class zahrom1111(BaseConfig):
    UNDERLYING_NAME = "اهرم"
    UNDERLYING_TICKER = "IRT1AHRM0001"
    OPTION_NAME = "ضهرم1111"
    OPTION_TICKER = "IRO9AHRM2811"
    EXPIRATION_DATE = "1403-11-24"
    STRIKE_PRICE = 28000


class zahrom1110(BaseConfig):
    UNDERLYING_NAME = "اهرم"
    UNDERLYING_TICKER = "IRT1AHRM0001"
    OPTION_NAME = "ضهرم1110"
    OPTION_TICKER = "IRO9AHRM2551"
    EXPIRATION_DATE = "1403-11-24"
    STRIKE_PRICE = 26000


class tahrom1112(BaseConfig):
    UNDERLYING_NAME = "اهرم"
    UNDERLYING_TICKER = "IRT1AHRM0001"
    OPTION_NAME = "طهرم1112"
    OPTION_TICKER = "IROFAHRM3821"
    EXPIRATION_DATE = "1403-11-24"
    STRIKE_PRICE = 30000


class tahrom1111(BaseConfig):
    UNDERLYING_NAME = "اهرم"
    UNDERLYING_TICKER = "IRT1AHRM0001"
    OPTION_NAME = "طهرم1111"
    OPTION_TICKER = "IROFAHRM3811"
    EXPIRATION_DATE = "1403-11-24"
    STRIKE_PRICE = 28000


# Map modes to configurations
CONFIGS = {
    'zahrom1110': zahrom1110,
    'zahrom1111': zahrom1111,
    'tahrom1111': tahrom1111,
    'tahrom1112': tahrom1112,
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
