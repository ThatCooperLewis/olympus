import logging

################# General #################

LOGGING_LEVEL = logging.INFO
'''Tells the logging module to only report messages of a certain level (INFO, DEBUG, ERROR).'''

CREDENTIALS_FILE = 'credentials.json'
'''Contains API keys, webhook URLs, PSQL connection, etc. See readme.md for more information.'''

################# Postgres #################

POSTGRES_TICKER_TABLE_NAME = 'ticker_feed'
'''The name of the pSQL table that stores live ticker data.'''

POSTGRES_ORDER_TABLE_NAME = 'order_feed'
'''The name of the pSQL table that stores order data & history.'''

POSTGRES_ORDER_STATUS_QUEUED = 'QUEUED'
'''The postgres.order_feed status of an order that has been queued for execution.'''

POSTGRES_ORDER_STATUS_PROCESSING = 'PROCESSING'
'''The postgres.order_feed status of an order that is currently being processed.'''

POSTGRES_ORDER_STATUS_COMPLETE = 'COMPLETE'
'''The postgres.order_feed status of an order that has been completed.'''

################# Scraping #################

TICKER_INTERVAL = 60  # seconds
'''Number of seconds between tickers in source data, or the interval which to scrape them'''

SOCKET_TIMEOUT_INTERVAL_MULTIPLIER = 2
'''Multiplies the TICKER_INTERVAL for length of time without any new data from ticker scraper before we attempt a socket reconnect'''

################# Trading #################

MAX_TRADE_PERCENTAGE = .2
'''Maximum percentage of total balance to spend on a single trade'''

CRYPTO_SYMBOL = 'BTC_TR'
'''The symbol of the cryptocurrency when checking account balance'''

FIAT_SYMBOL = 'USD'
'''The symbol of the fiat currency to check in account balance'''

TRADING_SYMBOL = 'BTCUSD_TR'
'''The symbol of the trading pair to trade, used when creating Order objects'''

################# Crosstower API #################

DEFAULT_CURRENCY = 'BTC'
'''[]The default currency to use when making API market requests'''

DEFAULT_SYMBOL = 'BTCUSD'
'''[UNUSED] The default symbol to use when making API market requests, representing the trading pair'''

REST_URL = 'https://api.crosstower.com/api/2'
'''The base REST URL for the crosstower API'''

SOCKET_URI = 'wss://api.crosstower.com/api/2/ws'
'''The base socket URL for the crosstower API'''

################# Model Training #################

SEQUENCE_LENGTH = 20
'''The number of time steps to use in the LSTM model'''

DROPOUT = 0.2
'''The dropout rate to use when training the model'''

EPOCH_COUNT = 50
'''The number of epochs to train the model for.'''

TESTING_SPLIT = 0.95
'''The percentage of the data to use for testing.'''

VALIDATION_SPLIT = 0.2
'''The percentage of the data to use for validation.'''

################# Prediction #################

PREDICTION_DELTA_THRESHOLD = 0.0003
'''When price is predicted to change by this much percentage, take 100% action'''

PREDICTION_ITERATION_COUNT = 3
'''The number of prediction cycles to run before stopping & submitting prediction.'''