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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/131.0.0.0 Safari/537.36',
        # Empty User-Agent
        'Accept': 'application/json, text/plain, */*',
        'Cookie': 'cookiesession1=678B2928B1B3FC87D21EEC7CB0BB44AB; otauth-178-OMSfe1c694d-b123-4d09-b395-01304776fae4=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJTZXNzaW9uSWQiOiJmZTFjNjk0ZC1iMTIzLTRkMDktYjM5NS0wMTMwNDc3NmZhZTQiLCJVc2VySWQiOiIxMDA3OTUiLCJBcHBOYW1lIjoiT01TIiwiQnJva2VyQ29kZSI6IjE3OCIsIm5iZiI6MTczOTczODk2MSwiZXhwIjoxNzM5NzY3NzYxLCJpc3MiOiJPTVMiLCJhdWQiOiJPTVMifQ.QtZyiXf3ReIxVhLXORMk3O6psLkNhhF9U3A3Ag_HSoEyl-_VgXN4zDTX-Xbbgo8crAFIhT9Q0pUCvhrpl70qeQ',
        'x-sessionId': 'OMSfe1c694d-b123-4d09-b395-01304776fae4',
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
    ORDER_PRICE = 1000000 // 100
    MAX_BID = 50000000 * 10
    NET_WORTH = 0
    DELTA_BUY_MIN = 0.3
    DELTA_BUY_MAX = 1.0  # Since Call option Delta is always between 0 and 1

    DELTA_SELL_MIN = -1.0  # Since Put option Delta is between -1 and 0
    DELTA_SELL_MAX = -0.3

    HISTORICAL_DATA_START_DATE = (jdatetime.date.today() - jdatetime.timedelta(days=4)).strftime('%Y-%m-%d')
    HISTORICAL_DATA_END_DATE = jdatetime.date.today().strftime('%Y-%m-%d')

    UNDERLYING_NAME = "خودرو"
    UNDERLYING_TICKER = "IRO1IKCO0001"

    MIN_REMAINING_DAYS = 14  # Minimum required days before expiration
    MIN_VOLUME_LIMIT = 40000  # Minimum volume required
    CAN_TRADE_IN_SAME_DIRECTION = False  # Initially False, becomes True when conditions are met
    CONDITION_CHECK_INTERVAL = 10


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


class Option_takhod1239(BaseConfig):
    OPTION_NAME = "طخود1239"
    OPTION_TICKER = "IROFIKCO9Q51"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 4500
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1240(BaseConfig):
    OPTION_NAME = "طخود1240"
    OPTION_TICKER = "IROFIKCO9Q61"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 5000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0142(BaseConfig):
    OPTION_NAME = "طخود0142"
    OPTION_TICKER = "IROFIKCO9Q71"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 5000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1226(BaseConfig):
    OPTION_NAME = "طخود1226"
    OPTION_TICKER = "IROFIKCO9L01"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 1700
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1227(BaseConfig):
    OPTION_NAME = "طخود1227"
    OPTION_TICKER = "IROFIKCO9L11"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 1800
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1228(BaseConfig):
    OPTION_NAME = "طخود1228"
    OPTION_TICKER = "IROFIKCO9L21"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 1900
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1229(BaseConfig):
    OPTION_NAME = "طخود1229"
    OPTION_TICKER = "IROFIKCO9L31"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 2000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1230(BaseConfig):
    OPTION_NAME = "طخود1230"
    OPTION_TICKER = "IROFIKCO9L41"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 2200
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1231(BaseConfig):
    OPTION_NAME = "طخود1231"
    OPTION_TICKER = "IROFIKCO9L51"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 2400
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1232(BaseConfig):
    OPTION_NAME = "طخود1232"
    OPTION_TICKER = "IROFIKCO9L61"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 2600
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1233(BaseConfig):
    OPTION_NAME = "طخود1233"
    OPTION_TICKER = "IROFIKCO9L71"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 2800
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1234(BaseConfig):
    OPTION_NAME = "طخود1234"
    OPTION_TICKER = "IROFIKCO9L81"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 3000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1235(BaseConfig):
    OPTION_NAME = "طخود1235"
    OPTION_TICKER = "IROFIKCO9L91"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 3250
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1236(BaseConfig):
    OPTION_NAME = "طخود1236"
    OPTION_TICKER = "IROFIKCO9M01"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 3500
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1237(BaseConfig):
    OPTION_NAME = "طخود1237"
    OPTION_TICKER = "IROFIKCO9M11"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 3750
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod1238(BaseConfig):
    OPTION_NAME = "طخود1238"
    OPTION_TICKER = "IROFIKCO9M21"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 4000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0126(BaseConfig):
    OPTION_NAME = "طخود0126"
    OPTION_TICKER = "IROFIKCO9M31"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 1500
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0127(BaseConfig):
    OPTION_NAME = "طخود0127"
    OPTION_TICKER = "IROFIKCO9M41"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 1600
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0128(BaseConfig):
    OPTION_NAME = "طخود0128"
    OPTION_TICKER = "IROFIKCO9M51"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 1700
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0129(BaseConfig):
    OPTION_NAME = "طخود0129"
    OPTION_TICKER = "IROFIKCO9M61"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 1800
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0130(BaseConfig):
    OPTION_NAME = "طخود0130"
    OPTION_TICKER = "IROFIKCO9M71"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 1900
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0131(BaseConfig):
    OPTION_NAME = "طخود0131"
    OPTION_TICKER = "IROFIKCO9M81"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 2000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0132(BaseConfig):
    OPTION_NAME = "طخود0132"
    OPTION_TICKER = "IROFIKCO9M91"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 2200
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0133(BaseConfig):
    OPTION_NAME = "طخود0133"
    OPTION_TICKER = "IROFIKCO9N01"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 2400
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0134(BaseConfig):
    OPTION_NAME = "طخود0134"
    OPTION_TICKER = "IROFIKCO9N11"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 2600
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0135(BaseConfig):
    OPTION_NAME = "طخود0135"
    OPTION_TICKER = "IROFIKCO9N21"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 2800
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0136(BaseConfig):
    OPTION_NAME = "طخود0136"
    OPTION_TICKER = "IROFIKCO9N31"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 3000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0137(BaseConfig):
    OPTION_NAME = "طخود0137"
    OPTION_TICKER = "IROFIKCO9N41"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 3250
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0138(BaseConfig):
    OPTION_NAME = "طخود0138"
    OPTION_TICKER = "IROFIKCO9N51"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 3500
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2050(BaseConfig):
    OPTION_NAME = "طخود2050"
    OPTION_TICKER = "IROFIKCO9N61"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 2000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2051(BaseConfig):
    OPTION_NAME = "طخود2051"
    OPTION_TICKER = "IROFIKCO9N71"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 2200
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2052(BaseConfig):
    OPTION_NAME = "طخود2052"
    OPTION_TICKER = "IROFIKCO9N81"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 2400
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2053(BaseConfig):
    OPTION_NAME = "طخود2053"
    OPTION_TICKER = "IROFIKCO9N91"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 2600
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2054(BaseConfig):
    OPTION_NAME = "طخود2054"
    OPTION_TICKER = "IROFIKCO9O11"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 2800
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2055(BaseConfig):
    OPTION_NAME = "طخود2055"
    OPTION_TICKER = "IROFIKCO9O21"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 3000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2056(BaseConfig):
    OPTION_NAME = "طخود2056"
    OPTION_TICKER = "IROFIKCO9O31"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 3250
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2057(BaseConfig):
    OPTION_NAME = "طخود2057"
    OPTION_TICKER = "IROFIKCO9O41"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 3500
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2058(BaseConfig):
    OPTION_NAME = "طخود2058"
    OPTION_TICKER = "IROFIKCO9O51"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 3750
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2059(BaseConfig):
    OPTION_NAME = "طخود2059"
    OPTION_TICKER = "IROFIKCO9O61"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 4000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2060(BaseConfig):
    OPTION_NAME = "طخود2060"
    OPTION_TICKER = "IROFIKCO9O71"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 4500
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod2061(BaseConfig):
    OPTION_NAME = "طخود2061"
    OPTION_TICKER = "IROFIKCO9O81"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 5000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0139(BaseConfig):
    OPTION_NAME = "طخود0139"
    OPTION_TICKER = "IROFIKCO9O91"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 3750
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0140(BaseConfig):
    OPTION_NAME = "طخود0140"
    OPTION_TICKER = "IROFIKCO9P01"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 4000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod0141(BaseConfig):
    OPTION_NAME = "طخود0141"
    OPTION_TICKER = "IROFIKCO9P11"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 4500
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3089(BaseConfig):
    OPTION_NAME = "طخود3089"
    OPTION_TICKER = "IROFIKCO9P21"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 2400
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3090(BaseConfig):
    OPTION_NAME = "طخود3090"
    OPTION_TICKER = "IROFIKCO9P31"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 2600
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3091(BaseConfig):
    OPTION_NAME = "طخود3091"
    OPTION_TICKER = "IROFIKCO9P41"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 2800
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3092(BaseConfig):
    OPTION_NAME = "طخود3092"
    OPTION_TICKER = "IROFIKCO9P51"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 3000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3093(BaseConfig):
    OPTION_NAME = "طخود3093"
    OPTION_TICKER = "IROFIKCO9P61"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 3250
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3094(BaseConfig):
    OPTION_NAME = "طخود3094"
    OPTION_TICKER = "IROFIKCO9P71"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 3500
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3095(BaseConfig):
    OPTION_NAME = "طخود3095"
    OPTION_TICKER = "IROFIKCO9P81"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 3750
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3096(BaseConfig):
    OPTION_NAME = "طخود3096"
    OPTION_TICKER = "IROFIKCO9P91"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 4000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3097(BaseConfig):
    OPTION_NAME = "طخود3097"
    OPTION_TICKER = "IROFIKCO9Q01"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 4500
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3098(BaseConfig):
    OPTION_NAME = "طخود3098"
    OPTION_TICKER = "IROFIKCO9Q11"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 5000
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_takhod3099(BaseConfig):
    OPTION_NAME = "طخود3099"
    OPTION_TICKER = "IROFIKCO9Q21"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 5500
    CALL_PUT = 'p'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1239(BaseConfig):
    OPTION_NAME = "ضخود1239"
    OPTION_TICKER = "IRO9IKCO8Q51"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 4500
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1240(BaseConfig):
    OPTION_NAME = "ضخود1240"
    OPTION_TICKER = "IRO9IKCO8Q61"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 5000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0142(BaseConfig):
    OPTION_NAME = "ضخود0142"
    OPTION_TICKER = "IRO9IKCO8Q71"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 5000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3089(BaseConfig):
    OPTION_NAME = "ضخود3089"
    OPTION_TICKER = "IRO9IKCO8P21"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 2400
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3090(BaseConfig):
    OPTION_NAME = "ضخود3090"
    OPTION_TICKER = "IRO9IKCO8P31"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 2600
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3091(BaseConfig):
    OPTION_NAME = "ضخود3091"
    OPTION_TICKER = "IRO9IKCO8P41"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 2800
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3092(BaseConfig):
    OPTION_NAME = "ضخود3092"
    OPTION_TICKER = "IRO9IKCO8P51"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 3000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3093(BaseConfig):
    OPTION_NAME = "ضخود3093"
    OPTION_TICKER = "IRO9IKCO8P61"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 3250
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3094(BaseConfig):
    OPTION_NAME = "ضخود3094"
    OPTION_TICKER = "IRO9IKCO8P71"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 3500
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3095(BaseConfig):
    OPTION_NAME = "ضخود3095"
    OPTION_TICKER = "IRO9IKCO8P81"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 3750
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3096(BaseConfig):
    OPTION_NAME = "ضخود3096"
    OPTION_TICKER = "IRO9IKCO8P91"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 4000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3097(BaseConfig):
    OPTION_NAME = "ضخود3097"
    OPTION_TICKER = "IRO9IKCO8Q01"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 4500
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3098(BaseConfig):
    OPTION_NAME = "ضخود3098"
    OPTION_TICKER = "IRO9IKCO8Q11"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 5000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod3099(BaseConfig):
    OPTION_NAME = "ضخود3099"
    OPTION_TICKER = "IRO9IKCO8Q21"
    EXPIRATION_DATE = "1404-03-07"
    STRIKE_PRICE = 5500
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0139(BaseConfig):
    OPTION_NAME = "ضخود0139"
    OPTION_TICKER = "IRO9IKCO8O91"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 3750
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0140(BaseConfig):
    OPTION_NAME = "ضخود0140"
    OPTION_TICKER = "IRO9IKCO8P01"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 4000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0141(BaseConfig):
    OPTION_NAME = "ضخود0141"
    OPTION_TICKER = "IRO9IKCO8P11"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 4500
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1226(BaseConfig):
    OPTION_NAME = "ضخود1226"
    OPTION_TICKER = "IRO9IKCO8L01"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 1700
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1227(BaseConfig):
    OPTION_NAME = "ضخود1227"
    OPTION_TICKER = "IRO9IKCO8L11"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 1800
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1228(BaseConfig):
    OPTION_NAME = "ضخود1228"
    OPTION_TICKER = "IRO9IKCO8L21"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 1900
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1229(BaseConfig):
    OPTION_NAME = "ضخود1229"
    OPTION_TICKER = "IRO9IKCO8L31"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 2000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1230(BaseConfig):
    OPTION_NAME = "ضخود1230"
    OPTION_TICKER = "IRO9IKCO8L41"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 2200
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1231(BaseConfig):
    OPTION_NAME = "ضخود1231"
    OPTION_TICKER = "IRO9IKCO8L51"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 2400
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1232(BaseConfig):
    OPTION_NAME = "ضخود1232"
    OPTION_TICKER = "IRO9IKCO8L61"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 2600
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1233(BaseConfig):
    OPTION_NAME = "ضخود1233"
    OPTION_TICKER = "IRO9IKCO8L71"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 2800
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1234(BaseConfig):
    OPTION_NAME = "ضخود1234"
    OPTION_TICKER = "IRO9IKCO8L81"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 3000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1235(BaseConfig):
    OPTION_NAME = "ضخود1235"
    OPTION_TICKER = "IRO9IKCO8L91"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 3250
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1236(BaseConfig):
    OPTION_NAME = "ضخود1236"
    OPTION_TICKER = "IRO9IKCO8M01"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 3500
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1237(BaseConfig):
    OPTION_NAME = "ضخود1237"
    OPTION_TICKER = "IRO9IKCO8M11"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 3750
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod1238(BaseConfig):
    OPTION_NAME = "ضخود1238"
    OPTION_TICKER = "IRO9IKCO8M21"
    EXPIRATION_DATE = "1403-12-01"
    STRIKE_PRICE = 4000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2050(BaseConfig):
    OPTION_NAME = "ضخود2050"
    OPTION_TICKER = "IRO9IKCO8N61"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 2000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2051(BaseConfig):
    OPTION_NAME = "ضخود2051"
    OPTION_TICKER = "IRO9IKCO8N71"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 2200
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2052(BaseConfig):
    OPTION_NAME = "ضخود2052"
    OPTION_TICKER = "IRO9IKCO8N81"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 2400
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2053(BaseConfig):
    OPTION_NAME = "ضخود2053"
    OPTION_TICKER = "IRO9IKCO8N91"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 2600
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2054(BaseConfig):
    OPTION_NAME = "ضخود2054"
    OPTION_TICKER = "IRO9IKCO8O11"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 2800
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2055(BaseConfig):
    OPTION_NAME = "ضخود2055"
    OPTION_TICKER = "IRO9IKCO8O21"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 3000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2056(BaseConfig):
    OPTION_NAME = "ضخود2056"
    OPTION_TICKER = "IRO9IKCO8O31"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 3250
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2057(BaseConfig):
    OPTION_NAME = "ضخود2057"
    OPTION_TICKER = "IRO9IKCO8O41"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 3500
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2058(BaseConfig):
    OPTION_NAME = "ضخود2058"
    OPTION_TICKER = "IRO9IKCO8O51"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 3750
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2059(BaseConfig):
    OPTION_NAME = "ضخود2059"
    OPTION_TICKER = "IRO9IKCO8O61"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 4000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2060(BaseConfig):
    OPTION_NAME = "ضخود2060"
    OPTION_TICKER = "IRO9IKCO8O71"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 4500
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod2061(BaseConfig):
    OPTION_NAME = "ضخود2061"
    OPTION_TICKER = "IRO9IKCO8O81"
    EXPIRATION_DATE = "1404-02-03"
    STRIKE_PRICE = 5000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0126(BaseConfig):
    OPTION_NAME = "ضخود0126"
    OPTION_TICKER = "IRO9IKCO8M31"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 1500
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0127(BaseConfig):
    OPTION_NAME = "ضخود0127"
    OPTION_TICKER = "IRO9IKCO8M41"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 1600
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0128(BaseConfig):
    OPTION_NAME = "ضخود0128"
    OPTION_TICKER = "IRO9IKCO8M51"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 1700
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0129(BaseConfig):
    OPTION_NAME = "ضخود0129"
    OPTION_TICKER = "IRO9IKCO8M61"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 1800
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0130(BaseConfig):
    OPTION_NAME = "ضخود0130"
    OPTION_TICKER = "IRO9IKCO8M71"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 1900
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0131(BaseConfig):
    OPTION_NAME = "ضخود0131"
    OPTION_TICKER = "IRO9IKCO8M81"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 2000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0132(BaseConfig):
    OPTION_NAME = "ضخود0132"
    OPTION_TICKER = "IRO9IKCO8M91"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 2200
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0133(BaseConfig):
    OPTION_NAME = "ضخود0133"
    OPTION_TICKER = "IRO9IKCO8N01"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 2400
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0134(BaseConfig):
    OPTION_NAME = "ضخود0134"
    OPTION_TICKER = "IRO9IKCO8N11"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 2600
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0135(BaseConfig):
    OPTION_NAME = "ضخود0135"
    OPTION_TICKER = "IRO9IKCO8N21"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 2800
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0136(BaseConfig):
    OPTION_NAME = "ضخود0136"
    OPTION_TICKER = "IRO9IKCO8N31"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 3000
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0137(BaseConfig):
    OPTION_NAME = "ضخود0137"
    OPTION_TICKER = "IRO9IKCO8N41"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 3250
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


class Option_zakhod0138(BaseConfig):
    OPTION_NAME = "ضخود0138"
    OPTION_TICKER = "IRO9IKCO8N51"
    EXPIRATION_DATE = "1404-01-06"
    STRIKE_PRICE = 3500
    CALL_PUT = 'c'  # 'c' for call (kharid), 'p' for put (forosh)


# Map modes to configurations
CONFIGS = {
    'takhod1239': Option_takhod1239,
    'takhod1240': Option_takhod1240,
    'takhod0142': Option_takhod0142,
    'takhod1226': Option_takhod1226,
    'takhod1227': Option_takhod1227,
    'takhod1228': Option_takhod1228,
    'takhod1229': Option_takhod1229,
    'takhod1230': Option_takhod1230,
    'takhod1231': Option_takhod1231,
    'takhod1232': Option_takhod1232,
    'takhod1233': Option_takhod1233,
    'takhod1234': Option_takhod1234,
    'takhod1235': Option_takhod1235,
    'takhod1236': Option_takhod1236,
    'takhod1237': Option_takhod1237,
    'takhod1238': Option_takhod1238,
    'takhod0126': Option_takhod0126,
    'takhod0127': Option_takhod0127,
    'takhod0128': Option_takhod0128,
    'takhod0129': Option_takhod0129,
    'takhod0130': Option_takhod0130,
    'takhod0131': Option_takhod0131,
    'takhod0132': Option_takhod0132,
    'takhod0133': Option_takhod0133,
    'takhod0134': Option_takhod0134,
    'takhod0135': Option_takhod0135,
    'takhod0136': Option_takhod0136,
    'takhod0137': Option_takhod0137,
    'takhod0138': Option_takhod0138,
    'takhod2050': Option_takhod2050,
    'takhod2051': Option_takhod2051,
    'takhod2052': Option_takhod2052,
    'takhod2053': Option_takhod2053,
    'takhod2054': Option_takhod2054,
    'takhod2055': Option_takhod2055,
    'takhod2056': Option_takhod2056,
    'takhod2057': Option_takhod2057,
    'takhod2058': Option_takhod2058,
    'takhod2059': Option_takhod2059,
    'takhod2060': Option_takhod2060,
    'takhod2061': Option_takhod2061,
    'takhod0139': Option_takhod0139,
    'takhod0140': Option_takhod0140,
    'takhod0141': Option_takhod0141,
    'takhod3089': Option_takhod3089,
    'takhod3090': Option_takhod3090,
    'takhod3091': Option_takhod3091,
    'takhod3092': Option_takhod3092,
    'takhod3093': Option_takhod3093,
    'takhod3094': Option_takhod3094,
    'takhod3095': Option_takhod3095,
    'takhod3096': Option_takhod3096,
    'takhod3097': Option_takhod3097,
    'takhod3098': Option_takhod3098,
    'takhod3099': Option_takhod3099,
    'zakhod1239': Option_zakhod1239,
    'zakhod1240': Option_zakhod1240,
    'zakhod0142': Option_zakhod0142,
    'zakhod3089': Option_zakhod3089,
    'zakhod3090': Option_zakhod3090,
    'zakhod3091': Option_zakhod3091,
    'zakhod3092': Option_zakhod3092,
    'zakhod3093': Option_zakhod3093,
    'zakhod3094': Option_zakhod3094,
    'zakhod3095': Option_zakhod3095,
    'zakhod3096': Option_zakhod3096,
    'zakhod3097': Option_zakhod3097,
    'zakhod3098': Option_zakhod3098,
    'zakhod3099': Option_zakhod3099,
    'zakhod0139': Option_zakhod0139,
    'zakhod0140': Option_zakhod0140,
    'zakhod0141': Option_zakhod0141,
    'zakhod1226': Option_zakhod1226,
    'zakhod1227': Option_zakhod1227,
    'zakhod1228': Option_zakhod1228,
    'zakhod1229': Option_zakhod1229,
    'zakhod1230': Option_zakhod1230,
    'zakhod1231': Option_zakhod1231,
    'zakhod1232': Option_zakhod1232,
    'zakhod1233': Option_zakhod1233,
    'zakhod1234': Option_zakhod1234,
    'zakhod1235': Option_zakhod1235,
    'zakhod1236': Option_zakhod1236,
    'zakhod1237': Option_zakhod1237,
    'zakhod1238': Option_zakhod1238,
    'zakhod2050': Option_zakhod2050,
    'zakhod2051': Option_zakhod2051,
    'zakhod2052': Option_zakhod2052,
    'zakhod2053': Option_zakhod2053,
    'zakhod2054': Option_zakhod2054,
    'zakhod2055': Option_zakhod2055,
    'zakhod2056': Option_zakhod2056,
    'zakhod2057': Option_zakhod2057,
    'zakhod2058': Option_zakhod2058,
    'zakhod2059': Option_zakhod2059,
    'zakhod2060': Option_zakhod2060,
    'zakhod2061': Option_zakhod2061,
    'zakhod0126': Option_zakhod0126,
    'zakhod0127': Option_zakhod0127,
    'zakhod0128': Option_zakhod0128,
    'zakhod0129': Option_zakhod0129,
    'zakhod0130': Option_zakhod0130,
    'zakhod0131': Option_zakhod0131,
    'zakhod0132': Option_zakhod0132,
    'zakhod0133': Option_zakhod0133,
    'zakhod0134': Option_zakhod0134,
    'zakhod0135': Option_zakhod0135,
    'zakhod0136': Option_zakhod0136,
    'zakhod0137': Option_zakhod0137,
    'zakhod0138': Option_zakhod0138,
}
