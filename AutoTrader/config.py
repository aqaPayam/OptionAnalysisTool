import time

import pandas as pd
import jdatetime


class BaseConfig:
    # Shared settings across all modes
    BASE_URL = 'https://api-bbi.ephoenix.ir/api/v2'
    MARKET_URL = 'https://marketsheet1.ephoenix.ir/api'
    MDAPI_URL = 'https://mdapi1.ephoenix.ir/api/v2'

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/131.0.0.0 Safari/537.36',
        # Empty User-Agent
        'Accept': 'application/json, text/plain, */*',
        'Cookie': 'cookiesession1=678B2928B1B3FC87D21EEC7CB0BB44AB; otauth-178-OMSa1f4f9cb-197c-4a41-b4e7-d4602c4c83a7=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJTZXNzaW9uSWQiOiJhMWY0ZjljYi0xOTdjLTRhNDEtYjRlNy1kNDYwMmM0YzgzYTciLCJVc2VySWQiOiIxMDA3OTUiLCJBcHBOYW1lIjoiT01TIiwiQnJva2VyQ29kZSI6IjE3OCIsIm5iZiI6MTc0MjEwMzQ3OCwiZXhwIjoxNzQyMTMyMjc4LCJpc3MiOiJPTVMiLCJhdWQiOiJPTVMifQ.RRC0TZJK-KJzS7bHf3XlZly7sdxmTEN53BuR7OB_SG7GiCqqwmPk_OYD981EJfydl26w23yhWCANceaROnCLFA',
        'x-sessionId': 'OMSa1f4f9cb-197c-4a41-b4e7-d4602c4c83a7',
        'Content-Type': 'application/json',
    }

    RISK_FREE_RATE = 0.3
    USE_HISTORICAL = True
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
    ORDER_PRICE = 1_000_000 // 100
    MAX_BID = 25_000_000 * 10
    NET_WORTH = 0
    DELTA_MIN = 0.45
    VOLUME = 0

    HISTORICAL_DATA_START_DATE = (jdatetime.date.today() - jdatetime.timedelta(days=4)).strftime('%Y-%m-%d')
    HISTORICAL_DATA_END_DATE = jdatetime.date.today().strftime('%Y-%m-%d')

    TRADE_DIRECTION = 0  # float number , 0 for error values
    CURRENT_DELTA = None
    AVG_DELTA_BORDER = 0.1


class the_config(BaseConfig):
    UNDERLYING_NAME = ""
    UNDERLYING_TICKER = ""
    OPTION_NAME = ""
    OPTION_TICKER = ""
    EXPIRATION_DATE = ""
    STRIKE_PRICE = 0
    CALL_PUT = ''
    CAN_TRADE_IN_SAME_DIRECTION = False

    @classmethod
    def set_values(cls, underlying_name, underlying_ticker, option_name, option_ticker, expiration_date, strike_price,
                   call_put,
                   can_trade_in_same_direction):
        cls.UNDERLYING_NAME = underlying_name
        cls.UNDERLYING_TICKER = underlying_ticker
        cls.OPTION_NAME = option_name
        cls.OPTION_TICKER = option_ticker
        cls.EXPIRATION_DATE = expiration_date
        cls.STRIKE_PRICE = strike_price
        cls.CALL_PUT = call_put
        cls.CAN_TRADE_IN_SAME_DIRECTION = can_trade_in_same_direction


_config_instance = None


def get_config():
    global _config_instance
    if _config_instance is None:
        _config_instance = the_config()
    return _config_instance
