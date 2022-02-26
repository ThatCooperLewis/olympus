import logging

LOGGING_LEVEL = logging.INFO
'''Tells the logging module to only report messages of a certain level (INFO, DEBUG, ERROR).'''

CREDENTIALS_FILE = 'credentials.json'
'''Contains API keys, webhook URLs, PSQL connection, etc. See readme.md for more information.'''

# Postgres

POSTGRES_TICKER_TABLE_NAME = 'ticker_feed'

POSTGRES_ORDER_TABLE_NAME = 'order_feed'

# Scraping

TICKER_INTERVAL = 60  # seconds
'''Number of seconds between tickers in source data, or the interval which to scrape them'''

SOCKET_TIMEOUT_INTERVAL_MULTIPLIER = 2
'''Multiplies the TICKER_INTERVAL for length of time without any new data from ticker scraper before we attempt a socket reconnect'''

# Prediction

PREDICTION_DELTA_THRESHOLD = 0.0003
'''When price is predicted to change by this much percentage, take 100% action'''

PREDICTION_ITERATION_COUNT = 3
'''The number of prediction cycles to run before stopping & submitting prediction.'''

# Trading

MAX_TRADE_PERCENTAGE = .2
'''Maximum percentage of total balance to spend on a single trade'''

CRYPTO_SYMBOL = 'BTC_TR'
'''The symbol of the cryptocurrency when checking account balance'''

FIAT_SYMBOL = 'USD'
'''The symbol of the fiat currency to check in account balance'''

TRADING_SYMBOL = 'BTCUSD_TR'
'''The symbol of the trading pair to trade, used when creating Order objects'''

# TODO: Write comments for these
# Crosstower API

DEFAULT_CURRENCY = 'BTC'
DEFAULT_SYMBOL = 'BTCUSD'
REST_URL = 'https://api.crosstower.com/api/2'
SOCKET_URI = 'wss://api.crosstower.com/api/2/ws'

# Model Training

SEQUENCE_LENGTH = 20
DROPOUT = 0.2
EPOCH_COUNT = 50 
TESTING_SPLIT = 0.95
VALIDATION_SPLIT = 0.2