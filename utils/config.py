import logging


class General:

    STREAM_LOGGING_LEVEL = logging.DEBUG
    '''Tells the logging module to stream messages of a certain level to the CLI (INFO, DEBUG, ERROR).'''

    FILE_LOGGING_LEVEL = logging.DEBUG
    '''Tells the logging module to log a certain level to local file (INFO, DEBUG, ERROR).'''

    LOGGING_FILENAME = 'debug-log.txt'
    '''The name of the file to send logs.'''

    STATUS_UPDATE_INTERVAL = 21600 # 6 hours
    '''How often to update the status of the servers via discord, in seconds.'''

################# Google Drive  #################

class GoogleDrive:

    CREDENTIALS_PATH = 'google_creds.json'

    TOKEN_PATH = 'token.json'

    API_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    '''Defines the request permissions when accessing the Google Drive API.'''

    DAILY_FEED_RANGE = '_data!A2:H289'

    ALLTIME_FEED_RANGE = '_full_data!A2:D5002'

################# Postgres #################

class PostgresConfig:

    TICKER_TABLE_NAME = 'ticker_feed'
    '''The name of the pSQL table that stores live ticker data.'''

    TICKER_COLUMNS = '(timestamp, ask, bid, last, low, high, open, volume, volume_quote)'
    '''The columns of the pSQL table that stores live ticker data. Used for sql insert queries.'''

    TICKER_SELECT_NEWEST = "SELECT FLOOR(EXTRACT(EPOCH FROM timestamp)) AS timestamp_epoch, ask, bid, last, low, high, open, volume, volume_quote FROM ticker_feed ORDER BY timestamp_epoch DESC LIMIT %s"
    '''Used to select the newest rows from ticker_feed. Use '%' after this string to format a LIMIT number into the query'''

    ORDER_TABLE_NAME = 'order_feed'
    '''The name of the pSQL table that stores order data & history.'''

    ORDER_COLUMNS = '(timestamp, quantity, side, status, uuid, usd_balance, btc_balance, current_price)'
    '''The columns of the pSQL table that stores order data & history. Used for sql insert queries.'''

    PREDICTION_TABLE_NAME = 'prediction_feed'
    '''The name of the pSQL table that stores prediction data & history.'''

    PREDICTION_COLUMNS = '(timestamp, prediction_timestamp, prediction_weight, prediction_history, status, uuid, prediction_percent)'
    '''The columns of the pSQL table that stores prediction data & history. Used for sql insert queries.'''

    STATUS_QUEUED = 'QUEUED'
    '''The postgres.order_feed & prediction_feed status of a prediction that has been queued for order.'''

    STATUS_PROCESSING = 'PROCESSING'
    '''The postgres.order_feed & prediction_feed status of a prediction/order that is currently being processed.'''

    STATUS_COMPLETE = 'COMPLETE'
    '''The postgres.order_feed & prediction_feed status of an order that has been completed.'''

    STATUS_FAILED = 'FAILED'
    '''The postgres.order_feed & prediction_feed status of an order that has failed.'''

    ALLOWED_STATUSES = [STATUS_QUEUED, STATUS_PROCESSING, STATUS_COMPLETE, STATUS_FAILED]

    UNRESPONSIVE_TIMEOUT_THRESHOLD = 240
    '''Number of seconds before the monitoring service should give up sending alerts over an lack of table updates.'''

################# Ticker Scraper  #################

class ScraperConfig:

    TICKER_INTERVAL = 60  # seconds
    '''Number of seconds between tickers in source data, or the interval which to scrape them'''

    SOCKET_TIMEOUT_INTERVAL_MULTIPLIER = 2
    '''Multiplies the TICKER_INTERVAL for length of time without any new data from ticker scraper before we attempt a socket reconnect'''

    # For these headers, the prediction engine is looking for the "price" column in the table. 
    # 
    DEFAULT_ASK_CSV_HEADERS = 'price,bid,last,low,high,open,volume,volumeQuote,timestamp\n'
    '''The default headers to use when creating a new ask-based ticker/prediction CSV file'''
    
    DEFAULT_BID_CSV_HEADERS = 'ask,price,last,low,high,open,volume,volumeQuote,timestamp\n'
    '''The default headers to use when creating a new bid-based ticker/prediction CSV file'''

################# Hermes Trading #################

class TradingConfig:

    MAX_TRADE_PERCENTAGE = .4
    '''Maximum percentage of total balance to spend on a single trade'''

    CRYPTO_SYMBOL = 'BTC'
    '''The symbol of the cryptocurrency when checking account balance'''

    FIAT_SYMBOL = 'USD'
    '''The symbol of the fiat currency to check in account balance'''

    TRADING_SYMBOL = 'BTCUSD_TR'
    '''The symbol of the trading pair to trade, used when creating Order objects and fetching tickers'''

################# Crosstower API #################

class CrosstowerConfig:

    DEFAULT_CURRENCY = 'BTC'
    '''[]The default currency to use when making API market requests'''

    DEFAULT_SYMBOL = 'BTCUSD_TR'
    '''[UNUSED] The default symbol to use when making API market requests, representing the trading pair'''

    SOCKET_V3_URL = 'wss://api.us.crosstower.com/api/3/ws'
    '''The base socket URL for the Crosstower V3 API'''

################# Training #################

class TrainingConfig:

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

class PredictionConfig:

    PREDICTION_DELTA_THRESHOLD = 0.003
    '''When price is predicted to change by this much percentage, take 100% action'''

    PREDICTION_ITERATION_COUNT = 5
    '''The number of prediction cycles to run before stopping & submitting prediction.'''

    PREDICTION_QUEUE_MAX_SIZE = 5
    '''The maximum number of queued predictions before alerting'''

################# Robinhood #################

class RobinhoodConfig:
    
    LOGIN_URL = 'https://robinhood.com/login/'
    '''The URL to use when logging into Robinhood'''

    BTC_URL = 'https://robinhood.com/crypto/BTC/'