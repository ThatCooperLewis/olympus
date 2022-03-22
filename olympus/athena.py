import asyncio
import json
from queue import Queue
from threading import Thread
from time import sleep
from time import time as now
import traceback

from utils.config import DEFAULT_SYMBOL, SOCKET_URI, SOCKET_TIMEOUT_INTERVAL_MULTIPLIER
from crosstower.models import Ticker
from crosstower.socket_api import utils
from olympus.primordial_chaos import PrimordialChaos
from utils import Logger, DiscordWebhook, Postgres
from websockets import connect as Connection

class ConnectionException(Exception):
    pass

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
            self.symbol = DEFAULT_SYMBOL
        if custom_interval:
            self.interval = custom_interval
        else:
            self.interval = 1
        self.timeout_threshold = self.interval * SOCKET_TIMEOUT_INTERVAL_MULTIPLIER

    def restart_socket(self):
        self.log.debug('Restarting socket...')
        self.ticker_thread.join(timeout=5)
        self.connection_attempts += 1
        self.ticker_thread = Thread(target=self.ticker_loop, daemon=True)
        self.ticker_thread.start()

    async def __subscribe(self, socket: Connection):
        '''
        Send a subscribeTicker message to the
        socket, and wait for a response
        
        :param socket: Connection
        :type socket: Connection
        '''
        self.log.debug('Subscribing to socket...')
        data = {
            "method": "subscribeTicker",
            "params": {"symbol": self.symbol},
            "id": int(now())
        }
        await socket.send(json.dumps(data))

    async def __get_response(self, websocket: Connection, attempt_threshold = 3) -> Ticker:
        '''
        It takes a websocket, and attempts to receive a response from it. If it receives a response, it
        parses it and returns a Ticker object. If it doesn't receive a response, it returns None
        
        :param websocket: Connection
        :param attempt_threshold: The number of times the client will attempt to receive a response from the
        server before giving up, defaults to 3 (optional)
        :return: A Ticker object
        '''
        final_result = None
        response = None
        request_attempts = 0
        while True:
            try:
                response = await websocket.recv()
                break
            except Exception as err:
                trace = traceback.format_exc()
                self.log.debug(f'[__get_response] Error while awaiting response: {trace}')
                if request_attempts > attempt_threshold:
                    response = None
                    break
                else:
                    self.log.warn(f'[__get_response] Response timeout. Attempting to receive response again...')
                    request_attempts += 1
                    continue
        if response:
            final_result = utils.handle_response(response).get('params')
        else:
            self.alert_with_error(f'[__get_response] No response received after {attempt_threshold} attempts. Creating a new connection...')
            raise ConnectionException
        if final_result:
            return Ticker(final_result)
        else:
            self.log.debug('[__get_response] No final_result received from response (This is okay. Probably means no new data)')
        return None

    async def scrape_coroutine(self, connection_attempt: int, coroutine_restart_attempt: int = 0):
        '''
        This function is a asynchronous. It creates a connection to the websocket, subscribes to the ticker channel, 
        and then waits for a response from the websocket. If the response is a ticker, it is put into the queue
        
        :param connection_attempt: The current attempt number. Used to kill old connections.
        '''
        if coroutine_restart_attempt > 5:
            self.alert_with_error('[scrape_coroutine] Too many coroutine restarts. Killing coroutine...')
            return
        
        '''
        HELLO FUTURE COOPER
        Two central things here:
        websockets might suck
        websocket-client might be better? and its synchronous?
        Refactor to sync methods might be necessary here
        https://stackoverflow.com/questions/52692736/how-to-manually-close-a-websocket
        '''
        try_again = False
        async with Connection(SOCKET_URI) as websocket:
            await self.__subscribe(websocket)
            self.log.debug(f'Starting scrape attempt {connection_attempt}, coroutine attempt {coroutine_restart_attempt}')
            while not self.abort and self.connection_attempts == connection_attempt:
                try:
                    ticker = await self.__get_response(websocket)
                except ConnectionException:
                    self.log.debug('[scrape_coroutine] ConnectionException raised. Restarting socket...')
                    try_again = True
                    break
                if not ticker:
                    continue
                self.queue.put(ticker)
        if try_again:
            self.scrape_coroutine(self.connection_attempts, coroutine_restart_attempt+1)


    def ticker_loop(self):
        '''
        The function starts a new event loop, creates a coroutine object, 
        and runs the loop until the coroutine is complete
        '''
        try:
            self.log.debug('Starting ticker loop...')
            loop = asyncio.new_event_loop()
            attempt = int(self.connection_attempts)
            asyncio.set_event_loop(loop)
            future = asyncio.ensure_future(self.scrape_coroutine(attempt))
            loop.run_until_complete(future)
        except KeyboardInterrupt:
            self.log.debug('Keyboard interrupt received. Aborting...')
            loop.close()
            self.abort = True
        except Exception as err:
            self.alert_with_error(f'[ticker_loop] {err}\n{traceback.format_exc()}')
            loop.close()
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
            self.last_ticker = self.get_latest_ticker()
            self.last_time = now()
            self.log.debug('Running watchdog loop...')
            while not self.abort:
                current_ticker = self.get_latest_ticker()
                time_since_update = now() - self.last_time
                if current_ticker == self.last_ticker and time_since_update > self.timeout_threshold:
                    # TODO: Notify if several attempts don't work            
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
        except KeyboardInterrupt:
            self.log.debug('Keyboard interrupt received. Aborting...')
            self.abort = True
        except Exception as err:
            self.alert_with_error(f'[sql_loop] {err}\n{traceback.format_exc()}')
            raise err
        

    def handle_commands(self):
        print(utils.scraper_startup_message)
        try:
            while True:
                string = input("Enter command: ")
                if string.lower() in ['exit', 'e']:
                    print(utils.scraper_exit_message)
                    self.abort = True
                    break
                elif string.lower() in ['restart', 'r']:
                    print(utils.scraper_restart_message)
                    self.restart_socket()
                elif string.lower() in ['status', 's']:
                    utils.print_status_message(self.last_time, self.connection_attempts)
                elif string.lower() in ['help', 'h']:
                    print(utils.scraper_startup_message)
        except KeyboardInterrupt:
            self.log.debug('Keyboard interrupt received. Aborting...')
            self.abort = True
        except Exception as err:
            self.alert_with_error(f'[sql_loop] {err}\n{traceback.format_exc()}')
            raise err

    def get_latest_ticker(self):
        if self.csv_path:
            utils.get_newest_line(self.csv_path)
        else:
            latest = self.postgres.get_latest_tickers(row_count=1)
            if type(latest) is list and len(latest) > 0:
                return latest[0]
            else:
                return None

    def run(self, headless: bool = False):
        PrimordialChaos.run(self)
        if not headless:
            self.log.debug('Running in interactive mode...')
            self.handle_commands()
