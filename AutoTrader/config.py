# config.py

import pandas as pd

# API Endpoints
BASE_URL = 'https://api-bbi.ephoenix.ir/api/v2'
MARKET_URL = 'https://marketsheet1.ephoenix.ir/api'
MDAPI_URL = 'https://mdapi1.ephoenix.ir/api/v2'

# API Headers
HEADERS = {
    'User-Agent': 'Your User Agent',
    'Accept': 'application/json, text/plain, */*',
    'Cookie': 'Your Cookie',  # Set securely
    'x-sessionId': 'Your Session ID',  # Set securely
    'Content-Type': 'application/json'
}

# Tickers
UNDERLYING_TICKER = "IRT1AHRM0001"  # Replace with actual ticker
OPTION_TICKER = "IRO9AHRM8891"      # Replace with actual ticker

# Trading Parameters
EXPIRATION_DATE = "1403-08-30"  # Jalali date (YYYY-MM-DD)
RISK_FREE_RATE = 0.3
STRIKE_PRICE = 18000
CALL_PUT = 'c'  # 'c' for call, 'p' for put

# Trading Session Time (Jalali Time)
VALID_TIME_START = pd.to_datetime("09:15:00").time()
VALID_TIME_END = pd.to_datetime("12:30:00").time()

# Retry and Sleep Configuration
MAX_RETRIES = 7
SLEEP_INTERVAL = 1  # seconds

# Volatility Smoothing Parameter
SMOOTHING_PARAM = 900  # e.g., 5 for SMA, 0.3 for EMA

# Rolling Window Size for Signal Generation
WINDOW_SIZE = 900  # Number of past price differences

# Z-score Threshold for Generating Signals
Z_THRESHOLD = 1.5  # Threshold for buy/sell signals

# Trading Parameters for Buy/Sell Functions
BUY_PRICE_OFFSET = -1  # Adjust as needed
SELL_PRICE_OFFSET = 1   # Adjust as needed
ORDER_QUANTITY = 1     # Adjust as per your requirements
TICKER = OPTION_TICKER  


