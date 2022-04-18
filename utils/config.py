import logging

################# General #################

STREAM_LOGGING_LEVEL = logging.INFO
'''Tells the logging module to stream messages of a certain level to the CLI (INFO, DEBUG, ERROR).'''

FILE_LOGGING_LEVEL = logging.DEBUG
'''Tells the logging module to log a certain level to local file (INFO, DEBUG, ERROR).'''

LOGGING_FILENAME = 'debug-log.txt'
'''The name of the file to send logs.'''

STATUS_UPDATE_INTERVAL = 21600 # 6 hours
'''How often to update the status of the servers via discord, in seconds.'''

################# Postgres #################

POSTGRES_TICKER_TABLE_NAME = 'ticker_feed'
'''The name of the pSQL table that stores live ticker data.'''

POSTGRES_TICKER_COLUMNS = '(timestamp, ask, bid, last, low, high, open, volume, volume_quote)'
'''The columns of the pSQL table that stores live ticker data. Used for sql insert queries.'''

POSTGRES_ORDER_TABLE_NAME = 'order_feed'
'''The name of the pSQL table that stores order data & history.'''

POSTGRES_ORDER_COLUMNS = '(timestamp, quantity, side, status, uuid)'
'''The columns of the pSQL table that stores order data & history. Used for sql insert queries.'''

POSTGRES_PREDICTION_TABLE_NAME = 'prediction_feed'
'''The name of the pSQL table that stores prediction data & history.'''

POSTGRES_PREDICTION_COLUMNS = '(timestamp, prediction_timestamp, prediction_weight, prediction_history, status, uuid, prediction_percent)'
'''The columns of the pSQL table that stores prediction data & history. Used for sql insert queries.'''

POSTGRES_STATUS_QUEUED = 'QUEUED'
'''The postgres.order_feed status of a prediction that has been queued for order.'''

POSTGRES_STATUS_PROCESSING = 'PROCESSING'
'''The postgres.order_feed status of a prediction/order that is currently being processed.'''

POSTGRES_STATUS_COMPLETE = 'COMPLETE'
'''The postgres.order_feed status of an order that has been completed.'''

POSTGRES_STATUS_FAILED = 'FAILED'
'''The postgres.order_feed status of an order that has failed.'''

POSTGRES_ALLOWED_STATUSES = [POSTGRES_STATUS_QUEUED, POSTGRES_STATUS_PROCESSING, POSTGRES_STATUS_COMPLETE, POSTGRES_STATUS_FAILED]

UNRESPONSIVE_TIMEOUT_THRESHOLD = 240
'''Number of seconds before the monitoring service should give up sending alerts over an lack of table updates.'''

################# Scraping #################

TICKER_INTERVAL = 60  # seconds
'''Number of seconds between tickers in source data, or the interval which to scrape them'''

SOCKET_TIMEOUT_INTERVAL_MULTIPLIER = 2
'''Multiplies the TICKER_INTERVAL for length of time without any new data from ticker scraper before we attempt a socket reconnect'''

DEFAULT_CSV_HEADERS = 'price,bid,last,low,high,open,volume,volumeQuote,timestamp\n'
'''The default headers to use when creating a new ticker/prediction CSV file'''

################# Trading #################

MAX_TRADE_PERCENTAGE = .4
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

PREDICTION_DELTA_THRESHOLD = 0.003
'''When price is predicted to change by this much percentage, take 100% action'''

PREDICTION_ITERATION_COUNT = 5
'''The number of prediction cycles to run before stopping & submitting prediction.'''

PREDICTION_QUEUE_MAX_SIZE = 5
'''The maximum number of queued predictions before alerting'''