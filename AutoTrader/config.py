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
        'Cookie': 'cookiesession1=678B2928B1B3FC87D21EEC7CB0BB44AB; otauth-178-OMSf5437d4b-b221-4f49-9d52-5e1b27901186=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJTZXNzaW9uSWQiOiJmNTQzN2Q0Yi1iMjIxLTRmNDktOWQ1Mi01ZTFiMjc5MDExODYiLCJVc2VySWQiOiIxMDA3OTUiLCJBcHBOYW1lIjoiT01TIiwiQnJva2VyQ29kZSI6IjE3OCIsIm5iZiI6MTczNjE0MjMwMiwiZXhwIjoxNzM2MTcxMTAyLCJpc3MiOiJPTVMiLCJhdWQiOiJPTVMifQ.pgrpNPR4i_k6x3gbhwgIOBq_gza--ggTFw7cVD_fnxd8nlVIFICaaeesew__s_ewcLgQeXukRZWbtp_0lkhuag',
        # Empty Cookie
        'x-sessionId': 'OMSf5437d4b-b221-4f49-9d52-5e1b27901186',  # Empty x-sessionId
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


class AhromConfig(BaseConfig):
    UNDERLYING_NAME = "اهرم"
    UNDERLYING_TICKER = "IRT1AHRM0001"
    OPTION_NAME = "ضهرم1110"
    OPTION_TICKER = "IRO9AHRM2551"
    EXPIRATION_DATE = "1403-11-24"
    STRIKE_PRICE = 26000


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


class ZaspaConfig(BaseConfig):
    UNDERLYING_NAME = "خساپا"
    UNDERLYING_TICKER = "IRO1SIPA0001"
    OPTION_NAME = "ضسپا1027"
    OPTION_TICKER = "IRO9SIPA8781"
    EXPIRATION_DATE = "1403-10-26"
    STRIKE_PRICE = 3000


# Map modes to configurations
CONFIGS = {
    'ahrom': AhromConfig,
    'khodro': KhodroConfig,
    'shasta': ShastaConfig,
    'zaspa': ZaspaConfig,
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
