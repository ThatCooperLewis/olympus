import asyncio
import json
from queue import Queue
from threading import Thread
from time import time

from crosstower.config import DEFAULT_CURRENCY, DEFAULT_SYMBOL, SOCKET_URI
from crosstower.models import Symbol, Ticker
from crosstower.socket_api import utils
from websockets import connect as Connection


async def get_request(method: str, params: dict):
    async with Connection(SOCKET_URI) as websocket:
        data = {
            "method": method,
            "params": params,
            "id": 123  # TODO: make good ID generator
        }
        await websocket.send(json.dumps(data))
        response = json.loads(await websocket.recv())
        if response.get('error'):
            err = f"API responded with error {response['error']['code']}: '{response['error']['message']}'"
            raise Exception(err)
        return response.get('result')


async def get_currency(currency: str = DEFAULT_CURRENCY):
    async with Connection(SOCKET_URI) as websocket:
        data = {
            "method": "getCurrency",
            "params": {"currency": currency},
            "id": 123
        }
        await websocket.send(json.dumps(data))
        response = json.loads(await websocket.recv())
        if response.get('error'):
            err = f"API responded with error {response['error']['code']}: '{response['error']['message']}'"
            raise Exception(err)
        return response.get('result')


async def get_symbol(symbol: str = DEFAULT_SYMBOL) -> Symbol:
    async with Connection(SOCKET_URI) as websocket:
        data = {
            "method": "getSymbol",
            "params": {"symbol": symbol},
            "id": 123
        }
        await websocket.send(json.dumps(data))
        response = json.loads(await websocket.recv())
        if response.get('error'):
            err = f"API responded with error {response['error']['code']}: '{response['error']['message']}'"
            raise Exception(err)
        return Symbol(response.get('result'))


class TickerScraper:

    def __init__(self, symbol: str = DEFAULT_SYMBOL, interval: int = 1):
        self.symbol = symbol
        self.interval = interval
        self.queue = Queue()
        self.quit = False

    async def __subscribe(self, socket: Connection):
        data = {
            "method": "subscribeTicker",
            "params": {"symbol": self.symbol},
            "id": 123
        }
        await socket.send(json.dumps(data))

    async def __unsubscribe(self, socket: Connection):
        data = {
            "method": "unsubscribeTicker",
            "params": {"symbol": self.symbol},
            "id": 123
        }
        await socket.send(json.dumps(data))

    async def __get_response(self, websocket: Connection) -> Ticker:
        response = await websocket.recv()
        result = utils.handle_response(response).get('params')
        if not result:
            return None
        return Ticker(result)

    async def scrape_coroutine(self):
        async with Connection(SOCKET_URI) as websocket:
            await self.__subscribe(websocket)
            latest = None
            while True:
                ticker = await self.__get_response(websocket)
                if not ticker:
                    continue
                self.queue.put(ticker)

    def scrape_thread(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.ensure_future(self.scrape_coroutine())
            loop.run_forever()
        except KeyboardInterrupt:
            self.quit = True
        finally:
            print('Closing')
            loop.close()

    def run(self):
        scrape_thread = Thread(target=self.scrape_thread, daemon=True)
        scrape_thread.start()
        try:
            latest = None
            while not self.quit:
                if self.queue.qsize() > 0:
                    ticker: Ticker = self.queue.get()
                    if not latest or (ticker.timestamp - latest) >= self.interval:
                        latest = ticker.timestamp
                        # TODO: 
                        '''
                        Hello future cooper
                        Wow this throttler works real well
                        Just need to write it to a file
                        Look into doing this for the other subscriptions
                        See if we can get consistent/useful data

                        Look into replacing the thread with multiprocessing. Should be useful in future
                        '''

                        print(ticker.csv_line, end='   \r')
        except KeyboardInterrupt:
            pass
