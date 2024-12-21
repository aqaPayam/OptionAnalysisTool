import pandas as pd
import jdatetime


class BaseConfig:
    # Shared settings across all modes
    BASE_URL = 'https://api-bbi.ephoenix.ir/api/v2'
    MARKET_URL = 'https://marketsheet1.ephoenix.ir/api'
    MDAPI_URL = 'https://mdapi1.ephoenix.ir/api/v2'

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        # Empty User-Agent
        'Accept': 'application/json, text/plain, */*',
        'Cookie': 'cookiesession1=678B2928B1B3FC87D21EEC7CB0BB44AB; otauth-178-OMS8096cc0b-814f-4040-bd43-b6843fff32c0=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJTZXNzaW9uSWQiOiI4MDk2Y2MwYi04MTRmLTQwNDAtYmQ0My1iNjg0M2ZmZjMyYzAiLCJVc2VySWQiOiIxMDA3OTUiLCJBcHBOYW1lIjoiT01TIiwiQnJva2VyQ29kZSI6IjE3OCIsIm5iZiI6MTczNDc1OTc4NCwiZXhwIjoxNzM0Nzg4NTg0LCJpc3MiOiJPTVMiLCJhdWQiOiJPTVMifQ.Ox-22Jh2e1beqBoCqqltHUwvQwYr0GIwWfvU8m4Vf9jEYVrMXhCEf9jY0CVM7ugnr-RRx6QXh3vnX6DVkep-Yw',
        # Empty Cookie
        'x-sessionId': 'OMS8096cc0b-814f-4040-bd43-b6843fff32c0',  # Empty x-sessionId
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
    ORDER_QUANTITY = 1

    HISTORICAL_DATA_START_DATE = (jdatetime.date.today() - jdatetime.timedelta(days=4)).strftime('%Y-%m-%d')
    HISTORICAL_DATA_END_DATE = jdatetime.date.today().strftime('%Y-%m-%d')
    SAVE_FOLDER = 'data_files'
    JUST_DOWNLOAD = False


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


def get_config():
    import os
    mode = os.getenv('APP_MODE', 'ahrom')  # Default mode is 'ahrom'
    return CONFIGS.get(mode, AhromConfig)()
