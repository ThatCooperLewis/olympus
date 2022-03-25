import asyncio
import json
from time import time as now

from utils.config import DEFAULT_CURRENCY, DEFAULT_SYMBOL, SOCKET_URI
from crosstower.models import Symbol
from crosstower.socket_api import utils
from websockets import connect as Connection
from websocket import create_connection, WebSocket

class MarketData:

    def __init__(self) -> None:
        return

    async def request(self, method: str, params: dict):
        # TODO: I'm pretty this is unused, maybe because it reopens a connection every time? Maybe optional connection override?
        async with Connection(SOCKET_URI) as websocket:
            data = {
                "method": method,
                "params": params,
                "id": int(now())
            }
            await websocket.send(json.dumps(data))
            response = json.loads(await websocket.recv())
            return utils.handle_response(response).get('result')

    def __request_until_complete(self, method: str, params: str):
        return asyncio.get_event_loop().run_until_complete(self.request(method, params))

    def get_currency(self, currency: str = DEFAULT_CURRENCY):
        currency = self.__request_until_complete(
            method='getCurrency',
            params={'currency': currency}
        )
        return currency

    def get_symbol(self, symbol: str = DEFAULT_SYMBOL) -> Symbol:
        symbol = self.__request_until_complete(
            method='getSymbol',
            params={'symbol': symbol}
        )
        return Symbol(symbol)


class TickerWebsocket:

    def __init__(self, symbol: str = DEFAULT_SYMBOL, uri: str = SOCKET_URI) -> None:
        self.symbol = symbol
        self.uri = uri
        self.connection: WebSocket = None

    def subscribe(self) -> bool:
        '''
        Starts subscription to ticker stream, returns True if successful
        '''
        self.connection = create_connection(self.uri)
        self.connection.send(json.dumps({
            "method": "subscribeTicker",
            "params": {"symbol": self.symbol},
            "id": int(now())
        }))
        result = self.connection.recv()
        return json.loads(result).get('result')

    def reconnect(self) -> bool:
        '''
        Closes existing socket connection, if it exists, and attempts to reconnect.
        Returns True if successful.
        '''
        if self.connection:
            self.connection.close()
        return self.subscribe()

    def get_ticker(self) -> str:
        '''
        Synchronously retrieves ticker data from the queue.
        '''
        return self.connection.recv()

    def stop(self) -> None:
        self.connection.close()
    