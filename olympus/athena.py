import asyncio
import json
from queue import Queue
from threading import Thread
from time import sleep
from time import time as now

from crosstower.config import DEFAULT_SYMBOL, SOCKET_URI
from crosstower.models import Ticker
from crosstower.socket_api import utils
from olympus.primordial_chaos import PrimordialChaos
from utils import Logger, DiscordWebhook
from websockets import connect as Connection

# Number of seconds without any new data before attempt a socket reconnect
SOCKET_RESTART_TIMEOUT = 20

class Athena(PrimordialChaos):
    '''
    Scrape CrossTower API for crypto price history
    '''

    def __init__(self, csv_path: str, custom_symbol: str = None, custom_interval: int = 1):
        super().__init__()
        self.log = Logger.setup(__name__)
        self.discord = DiscordWebhook('Athena')
        self.csv_path = csv_path
        self.queue = Queue()
        # Counts the number of attempts to connect to socket.
        # Used to kill old connections
        self.connection_attempts: int = 0
        # Set timestamp for last update
        self.last_time = now()

        # Watch for new tickers in queue
        self.csv_thread: Thread = Thread(target=self.csv_loop)
        # Constantly fetch new tickers
        self.ticker_thread: Thread = Thread(target=self.ticker_loop, daemon=True)
        # Make sure lines are being added to the spreadsheet
        self.watchdog_thread: Thread = Thread(target=self.watchdog_loop)
        # Add them all to superclass so they can be started/stopped
        self.all_threads = [self.csv_thread, self.ticker_thread, self.watchdog_thread]

        if custom_symbol:
            self.symbol = custom_symbol
        else:
            self.symbol = DEFAULT_SYMBOL
        if custom_interval:
            self.interval = custom_interval
        else:
            self.interval = 1

    def restart_socket(self):
        self.ticker_thread.join(timeout=5)
        self.connection_attempts += 1
        self.ticker_thread = Thread(target=self.ticker_loop, daemon=True)
        self.ticker_thread.start()
        # Remove old socket connection
        # self.all_threads.append()
        self.log.debug('Restarting socket...')
        # self.ticker_thread = new_thread
        # self.ticker_thread.start()

    async def __subscribe(self, socket: Connection):
        # TODO: Wrap in try/except
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
        # TODO: Wrap in try/except
        final_result = None
        response = None
        while True:
            request_attempts = 0
            try:
                response = await websocket.recv()
                break
            except Exception as err:
                self.alert_with_error(f'[__get_response] Error while awaiting response: {err.__traceback__}')
                if request_attempts > attempt_threshold:
                    response = None
                    break
                else:
                    self.log.warning(f'[__get_response] Response timeout. Attempting to receive response again...')
                    request_attempts += 1
                    continue
        if response:
            final_result = utils.handle_response(response).get('params')
        else:
            self.alert_with_error(f'[__get_response] No response received after {attempt_threshold} attempts')
        if final_result:
            return Ticker(final_result)
        else:
            self.log.debug('[__get_response] No final_result received from response (This is okay. Probably means no new data)')
        return None

    async def scrape_coroutine(self, current_attempt):
        '''
        This function is a asynchronous. It creates a connection to the websocket, subscribes to the ticker channel, 
        and then waits for a response from the websocket. If the response is a ticker, it is put into the queue
        
        :param current_attempt: The current attempt number. Used to kill old connections.
        '''
        # TODO: Wrap in try/except
        async with Connection(SOCKET_URI) as websocket:
            await self.__subscribe(websocket)
            self.log.debug(f'Starting scrape attempt {current_attempt}')
            while not self.abort and self.connection_attempts == current_attempt:
                ticker = await self.__get_response(websocket)
                if not ticker:
                    continue
                self.queue.put(ticker)
            return

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
            self.log.error(f'[ticker_loop] {err}\n{err.__traceback__}')
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
        self.last_line = utils.get_newest_line(self.csv_path)
        self.last_time = now()
        self.log.debug('Running watchdog loop...')
        # TODO: Wrap in try/except
        while not self.abort:
            current_line = utils.get_newest_line(self.csv_path)
            time_since_update = now() - self.last_time
            if current_line == self.last_line and time_since_update > SOCKET_RESTART_TIMEOUT:
                # TODO: Notify if several attempts don't work            
                self.log.warn(f'No new data received for {SOCKET_RESTART_TIMEOUT} seconds. Restarting socket...')    
                self.restart_socket()
            elif current_line != self.last_line:
                self.last_line = current_line
                self.last_time = now()
            sleep(5)

    def csv_loop(self):
        '''
        If the queue is populated, get the ticker from the queue, 
        and if the ticker's timestamp is more than
        interval seconds away from the latest timestamp,
        then write the ticker to the csv file
        '''
        latest = None
        # TODO: Wrap in try/except
        self.log.debug('Running CSV loop...')
        while not self.abort:
            if self.queue.qsize() > 0:
                ticker: Ticker = self.queue.get()
                if not latest or (ticker.timestamp - latest) >= self.interval:
                    latest = ticker.timestamp
                    with open(self.csv_path, 'a') as file:
                        file.write(ticker.csv_line)
                        file.close()

    def handle_commands(self):
        print(utils.scraper_startup_message)
        # TODO: Wrap in try/except
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

    def run(self, headless: bool = False):
        PrimordialChaos.run(self)
        if not headless:
            self.log.debug('Running in interactive mode...')
            self.handle_commands()