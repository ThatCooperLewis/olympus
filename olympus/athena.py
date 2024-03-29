import os
import traceback
from queue import Queue
from threading import Thread
from time import sleep
from time import time as now

from crosstower.models import Ticker
from crosstower.socket_api.public import ConnectionException, TickerWebsocket
from utils import DiscordWebhook, Logger, Postgres
from utils.config import CrosstowerConfig, ScraperConfig
from olympus.primordial_chaos import PrimordialChaos


class Athena(PrimordialChaos):
    '''
    Scrape CrossTower API for crypto price history
    '''

    def __init__(self, custom_csv_path: str = None, custom_symbol: str = None, custom_interval: int = 1):
        '''
        If csv_path is None, default SQL connection will be used
        '''
        super().__init__()
        self.log = Logger.setup(__name__)
        self.discord = DiscordWebhook('Athena')
        self.csv_path = custom_csv_path
        self.queue = Queue()
        # Counts the number of attempts to connect to socket.
        # Used to kill old connections
        self.connection_attempts: int = 0
        # Set timestamp for last update
        self.last_time = now()

        self.websocket = TickerWebsocket()

        # Constantly fetch new tickers
        self.ticker_thread: Thread = Thread(target=self.ticker_loop, daemon=True)
        # Make sure lines are being added to the spreadsheet
        self.watchdog_thread: Thread = Thread(target=self.watchdog_loop)
        # Add them all to superclass so they can be started/stopped
        if self.csv_path:
            self.csv_thread: Thread = Thread(target=self.csv_loop)
            self.all_threads = [self.csv_thread, self.ticker_thread, self.watchdog_thread]
        else:
            self.postgres = Postgres()
            self.sql_thread: Thread = Thread(target=self.sql_loop)
            self.all_threads = [self.sql_thread, self.ticker_thread, self.watchdog_thread]

        if custom_symbol:
            self.symbol = custom_symbol
        else:
            self.symbol = CrosstowerConfig.DEFAULT_SYMBOL
        if custom_interval:
            self.interval = custom_interval
        else:
            self.interval = 1
        self.timeout_threshold = self.interval * ScraperConfig.SOCKET_TIMEOUT_INTERVAL_MULTIPLIER

    def restart_socket(self):
        self.log.debug('Restarting socket...')
        self.ticker_thread.join(timeout=5)
        self.connection_attempts += 1
        self.ticker_thread = Thread(target=self.ticker_loop, daemon=True)
        self.ticker_thread.start()

    def __subscribe(self):
        '''
        Send a subscribeTicker message to the
        socket, and wait for a response
        
        :param socket: Connection
        :type socket: Connection
        '''
        self.log.debug('Subscribing to socket...')
        success = self.websocket.subscribe()
        if not success:
            self.alert_with_error('[__subscribe] Failed to subscribe to socket')
            raise ConnectionException

    def __get_response(self, attempt_threshold = 3) -> Ticker:
        '''
        It takes a websocket, and attempts to receive a response from it. If it receives a response, it
        parses it and returns a Ticker object. If it doesn't receive a response, it returns None
        
        :param websocket: Connection
        :param attempt_threshold: The number of times the client will attempt to receive a response from the
        server before giving up, defaults to 3 (optional)
        :return: A Ticker object
        '''
        request_attempts = 0
        while True:
            try:
                return self.websocket.get_ticker()
            except Exception as err:
                trace = traceback.format_exc()
                self.log.debug(f'[__get_response] Error while awaiting response: {trace}')
                if request_attempts > attempt_threshold:
                    raise ConnectionException
                else:
                    self.log.warn(f'[__get_response] Response timeout. Attempting to receive response again...')
                    request_attempts += 1
                    continue

    def __ticker_loop_attempt(self, connection_attempt: int, socket_restart_attempt: int = 0):
        '''
        This function is a asynchronous. It creates a connection to the websocket, subscribes to the ticker channel, 
        and then waits for a response from the websocket. If the response is a ticker, it is put into the queue
        
        :param connection_attempt: The current attempt number. Used to kill old connections.
        '''
        self.__subscribe()
        self.log.debug(f'Starting scrape attempt {connection_attempt}, coroutine attempt {socket_restart_attempt}')
        while not self.abort and self.connection_attempts == connection_attempt:
            if socket_restart_attempt > 5:
                self.alert_with_error('[__ticker_loop_attempt] Too many coroutine restarts. Killing coroutine...')
                self.abort = True
                return
            try:
                ticker = self.__get_response()
            except ConnectionException:
                self.log.debug('[__ticker_loop_attempt] ConnectionException raised. Restarting socket...')
                socket_restart_attempt += 1
                self.websocket.reconnect()
                continue
            if not ticker:
                continue
            self.queue.put(ticker)


    def ticker_loop(self):
        '''
        The function starts a new event loop, creates a coroutine object, 
        and runs the loop until the coroutine is complete
        '''
        try:
            self.log.debug('Starting ticker loop...')
            self.__ticker_loop_attempt(int(self.connection_attempts))
        except KeyboardInterrupt:
            self.log.debug('Keyboard interrupt received. Aborting...')
            self.abort = True
            self.websocket.stop()
        except Exception as err:
            self.alert_with_error(f'[ticker_loop] {err}\n{traceback.format_exc()}')
            self.websocket.stop()
            raise err

    def watchdog_loop(self):
        '''
        Monitor a running scraper. If the last line of the log file is the same as the current line, and the time since the last update
        is longer than the interval, then restart the socket
        
        :param path: The path to the log file
        :type path: str
        :param interval: How often to check for updates
        :type interval: int
        '''
        try:
            sleep(5)
            self.last_ticker = self.__get_latest_local_ticker()
            self.last_time = now()
            self.log.debug('Running watchdog loop...')
            while not self.abort:
                current_ticker = self.__get_latest_local_ticker()
                time_since_update = now() - self.last_time
                if current_ticker == self.last_ticker and time_since_update > self.timeout_threshold:
                    self.log.debug(f'No new data received for {self.timeout_threshold} seconds. Restarting socket...')    
                    self.restart_socket()
                elif current_ticker != self.last_ticker:
                    self.last_ticker = current_ticker
                    self.last_time = now()
                sleep(5)
        except KeyboardInterrupt:
            self.log.debug('Keyboard interrupt received. Aborting...')
            self.abort = True
        except Exception as err:
            self.alert_with_error(f'[watchdog_loop] {err}\n{traceback.format_exc()}')
            raise err

    def csv_loop(self):
        '''
        If the queue is populated, get the ticker from the queue, 
        and if the ticker's timestamp is more than
        interval seconds away from the latest timestamp,
        then write the ticker to the csv file
        '''
        # Make file if not exist
        if not os.path.exists(self.csv_path):
            self.log.debug(f'Creating csv file at {self.csv_path}')
            with open(self.csv_path, 'w') as csv_file:
                csv_file.write('')
        try:
            latest = None
            self.log.debug('Running CSV loop...')
            while not self.abort:
                if self.queue.qsize() > 0:
                    ticker: Ticker = self.queue.get()
                    if not latest or (ticker.timestamp - latest) >= self.interval:
                        latest = ticker.timestamp
                        with open(self.csv_path, 'a') as file:
                            file.write(ticker.csv_line)
                            file.close()
        except KeyboardInterrupt:
            self.log.debug('Keyboard interrupt received. Aborting...')
            self.abort = True
        except Exception as err:
            self.alert_with_error(f'[csv_loop] {err}\n{traceback.format_exc()}')
            raise err

    def sql_loop(self):
        """
        Get the latest ticker from the queue, if it's been at least
        self.interval seconds since the last ticker was inserted, insert it into the database
        """
        try:
            latest = None
            self.log.debug('Running SQL loop...')
            while not self.abort:
                if self.queue.qsize() > 0:
                    ticker: Ticker = self.queue.get()
                    if not latest or (ticker.timestamp - latest) >= self.interval:
                        latest = ticker.timestamp
                        self.postgres.insert_ticker(ticker)
                    sleep(1)
        except KeyboardInterrupt:
            self.log.debug('Keyboard interrupt received. Aborting...')
            self.abort = True
        except Exception as err:
            self.alert_with_error(f'[sql_loop] {err}\n{traceback.format_exc()}')
            raise err

    def __get_latest_local_ticker(self):
        if self.csv_path:
            with open(self.csv_path, 'rb') as f:
                for i in range(-2, 0):
                    try:
                        f.seek(i, os.SEEK_END)
                        while f.read(1) != b'\n':
                            f.seek(i, os.SEEK_CUR)
                        return f.readline().decode()
                    except OSError:
                        continue
                return ""
        else:
            latest = self.postgres.get_latest_tickers(row_count=1)
            if type(latest) is list and len(latest) > 0:
                return latest[0]
            else:
                return None
