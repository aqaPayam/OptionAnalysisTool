import pandas as pd
import jdatetime

# API Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Cookie': 'cookiesession1=678B28DD6FE6ED96910C335752DBC495; otauth-178-OMS937df03b-941d-40d6-a710-c63e62725897=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJTZXNzaW9uSWQiOiI5MzdkZjAzYi05NDFkLTQwZDYtYTcxMC1jNjNlNjI3MjU4OTciLCJVc2VySWQiOiIxMDA3OTUiLCJBcHBOYW1lIjoiT01TIiwiQnJva2VyQ29kZSI6IjE3OCIsIm5iZiI6MTczNDUwMDk4MCwiZXhwIjoxNzM0NTI5NzgwLCJpc3MiOiJPTVMiLCJhdWQiOiJPTVMifQ.OGhtDKu00qumKjc7-Ks7hb2dUXGDNZsvJrswTpXwufRUSjHiQveCLTnykFd8pTtphUwzz_8Y4mnAJwMIMyu3AA',
    # Set securely
    'x-sessionId': 'OMS937df03b-941d-40d6-a710-c63e62725897',  # Set securely
    'Content-Type': 'application/json'
}

UNDERLYING_NAME = "اهرم"
UNDERLYING_TICKER = "IRT1AHRM0001"  # Replace with actual ticker
OPTION_NAME = "ضهرم1007"
OPTION_TICKER = "IRO9AHRM2401"  # Replace with actual ticker
EXPIRATION_DATE = "1403-10-26"  # Jalali date (YYYY-MM-DD)
RISK_FREE_RATE = 0.3
STRIKE_PRICE = 18000
CALL_PUT = 'c'  # 'c' for call, 'p' for put

SMOOTHING_PARAM = 3600
WINDOW_SIZE = 3600
Z_THRESHOLD = 1.5

# API Endpoints
BASE_URL = 'https://api-bbi.ephoenix.ir/api/v2'
MARKET_URL = 'https://marketsheet1.ephoenix.ir/api'
MDAPI_URL = 'https://mdapi1.ephoenix.ir/api/v2'

USE_HISTORICAL = True
VALID_TIME_START = pd.to_datetime("09:15:00").time()
VALID_TIME_END = pd.to_datetime("12:30:00").time()
MAX_RETRIES = 7
SLEEP_INTERVAL = 1
MAX_SIZE = 10

BUY_PRICE_OFFSET = -1
SELL_PRICE_OFFSET = 1
ORDER_QUANTITY = 1
TICKER = OPTION_TICKER

HISTORICAL_DATA_START_DATE = (jdatetime.date.today() - jdatetime.timedelta(days=4)).strftime('%Y-%m-%d')
HISTORICAL_DATA_END_DATE = jdatetime.date.today().strftime('%Y-%m-%d')
