import asyncio
import json
from queue import Queue
from threading import Thread
from time import sleep
from time import time as now

from crosstower.config import DEFAULT_SYMBOL, SOCKET_URI
from crosstower.models import Ticker
from crosstower.socket_api import utils
from websockets import connect as Connection


class Athena:
    '''
    Scrape CrossTower API for crypto price history
    '''

    def __init__(self):
        self.queue = Queue()
        # Setting self.quitting to True will kill all threads. Cannot be undone
        self.quitting = False
        # Counts the number of attempts to connect to socket.
        # Used to kill old connections
        self.connection_attempts: int = 0
        # Apply default symbol and interval
        self.symbol = DEFAULT_SYMBOL
        self.interval = 1

    def __restart_socket(self):
        self.connection_attempts += 1
        Thread(target=self.ticker_loop, daemon=True).start()

    async def __subscribe(self, socket: Connection):
        data = {
            "method": "subscribeTicker",
            "params": {"symbol": self.symbol},
            "id": int(now())
        }
        await socket.send(json.dumps(data))

    async def __get_response(self, websocket: Connection) -> Ticker:
        final_result = None
        response = None
        while True:
            request_attempts = 0
            try:
                response = await websocket.recv()
                break
            except Exception as err:
                if request_attempts > 3:
                    response = None
                    break
                else:
                    request_attempts += 1
                    continue
        if response:
            final_result = utils.handle_response(response).get('params')
        if final_result:
            return Ticker(final_result)
        return None

    async def scrape_coroutine(self, current_attempt):
        async with Connection(SOCKET_URI) as websocket:
            await self.__subscribe(websocket)
            while not self.quitting and self.connection_attempts == current_attempt:
                ticker = await self.__get_response(websocket)
                if not ticker:
                    continue
                self.queue.put(ticker)
            return

    def ticker_loop(self):
        try:
            loop = asyncio.new_event_loop()
            attempt = int(self.connection_attempts)
            asyncio.set_event_loop(loop)
            future = asyncio.ensure_future(self.scrape_coroutine(attempt))
            loop.run_until_complete(future)
        except Exception as err:
            loop.close()
            raise err

    def watchdog_loop(self, path: str, interval: int):
        self.last_line = utils.get_newest_line(path)
        self.last_time = now()
        while not self.quitting:
            current_line = utils.get_newest_line(path)
            time_since_update = now() - self.last_time
            if current_line == self.last_line and time_since_update > interval:
                # TODO: Notify if several attempts don't work                
                self.__restart_socket()
            elif current_line != self.last_line:
                self.last_line = current_line
                self.last_time = now()
            sleep(5)

    def csv_loop(self, path):
        latest = None
        while not self.quitting:
            if self.queue.qsize() > 0:
                ticker: Ticker = self.queue.get()
                if not latest or (ticker.timestamp - latest) >= self.interval:
                    latest = ticker.timestamp
                    with open(path, 'a') as file:
                        file.write(ticker.csv_line)
                        file.close()

    def handle_commands(self):
        print(utils.scraper_startup_message)
        while True:
            string = input("Enter command: ")
            if string.lower() in ['exit', 'e']:
                print(utils.scraper_exit_message)
                self.quitting = True
                break
            elif string.lower() in ['restart', 'r']:
                print(utils.scraper_restart_message)
                self.__restart_socket()
            elif string.lower() in ['status', 's']:
                utils.print_status_message(self.last_time, self.connection_attempts)
            elif string.lower() in ['help', 'h']:
                print(utils.scraper_startup_message)

    def run(self, csv_path: str, custom_symbol: str = None, custom_interval: int = 1, headless: bool = False):
        if custom_symbol:
            self.symbol = custom_symbol
        if custom_interval:
            self.interval = custom_interval
        # Watch for new tickers in queue
        Thread(target=self.csv_loop, args=(csv_path,)).start()
        # Constantly fetch new tickers
        Thread(target=self.ticker_loop, daemon=True).start()
        # Make sure lines are being added to the spreadsheet
        Thread(target=self.watchdog_loop, args=(csv_path, 20)).start()
        if not headless:
            self.handle_commands()
