import pandas as pd
import jdatetime

# API Endpoints
BASE_URL = 'https://api-bbi.ephoenix.ir/api/v2'
MARKET_URL = 'https://marketsheet1.ephoenix.ir/api'
MDAPI_URL = 'https://mdapi1.ephoenix.ir/api/v2'

# API Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Cookie': 'cookiesession1=678B28DD6FE6ED96910C335752DBC495; otauth-178-OMS54415524-dcb6-44bb-a4ab-64a665fc64a8=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJTZXNzaW9uSWQiOiI1NDQxNTUyNC1kY2I2LTQ0YmItYTRhYi02NGE2NjVmYzY0YTgiLCJVc2VySWQiOiIxMDA3OTUiLCJBcHBOYW1lIjoiT01TIiwiQnJva2VyQ29kZSI6IjE3OCIsIm5iZiI6MTczNDMyNzk4NCwiZXhwIjoxNzM0MzU2Nzg0LCJpc3MiOiJPTVMiLCJhdWQiOiJPTVMifQ.BOotEZgxg6lxkwuKos8KYSXBaA-Ggf0gUivTq_AX68tQ9gYVBKBk6q0XG31VycfjEXHJkFlhmMELKR_0Robfew',
    # Set securely
    'x-sessionId': 'OMS54415524-dcb6-44bb-a4ab-64a665fc64a8',  # Set securely
    'Content-Type': 'application/json'
}

USE_HISTORICAL = True
# Tickers
UNDERLYING_NAME = "اهرم"
UNDERLYING_TICKER = "IRT1AHRM0001"  # Replace with actual ticker
OPTION_NAME = "ضهرم1007"
OPTION_TICKER = "IRO9AHRM2401"  # Replace with actual ticker

# Trading Parameters
EXPIRATION_DATE = "1403-10-26"  # Jalali date (YYYY-MM-DD)
RISK_FREE_RATE = 0.3
STRIKE_PRICE = 18000
CALL_PUT = 'c'  # 'c' for call, 'p' for put

# Trading Session Time (Jalali Time)
VALID_TIME_START = pd.to_datetime("09:15:00").time()
VALID_TIME_END = pd.to_datetime("12:30:00").time()

# Retry and Sleep Configuration
MAX_RETRIES = 7
SLEEP_INTERVAL = 1  # seconds
MAX_SIZE = 10

# Volatility Smoothing Parameter
SMOOTHING_PARAM = 3600  # e.g., 5 for SMA, 0.3 for EMA

# Rolling Window Size for Signal Generation
WINDOW_SIZE = 3600  # Number of past price differences

# Z-score Threshold for Generating Signals
Z_THRESHOLD = 1.5  # Threshold for buy/sell signals

# Trading Parameters for Buy/Sell Functions
BUY_PRICE_OFFSET = -1  # Adjust as needed
SELL_PRICE_OFFSET = 1  # Adjust as needed
ORDER_QUANTITY = 1  # Adjust as per your requirements
TICKER = OPTION_TICKER

# Inputs for process_and_flatten_market_data
HISTORICAL_DATA_START_DATE = '1403-09-24'  # Replace with actual start date
HISTORICAL_DATA_END_DATE = jdatetime.date.today().strftime('%Y-%m-%d')  # Set to today's date
SAVE_FOLDER = 'data_files'  # Folder to save data files
JUST_DOWNLOAD = False  # Set to True if you only want to download data
