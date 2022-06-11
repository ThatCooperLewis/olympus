import json
from time import time as now

from utils.config import CrosstowerConfig
from websocket import create_connection, WebSocket
from crosstower.socket_api.utils import handle_response
from crosstower.models import Ticker


class ConnectionException(Exception):
    pass


class TickerWebsocket:

    def __init__(self, symbol: str = CrosstowerConfig.DEFAULT_SYMBOL) -> None:
        self.symbol = symbol
        self.uri = CrosstowerConfig.SOCKET_V3_URL + '/public'
        self.connection: WebSocket = None

    def subscribe(self) -> bool:
        '''
        Starts subscription to ticker stream, returns True if successful
        '''
        self.connection = create_connection(self.uri)
        self.connection.send(json.dumps({
            "method": "subscribe",
            "ch": "ticker/1s/batch",
            "params": {
                "symbols": ["BTCUSD"]
            },
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

    def get_ticker(self) -> Ticker:
        '''
        Synchronously retrieves ticker data from the queue.
        '''
        response = self.connection.recv()
        if not response:
            raise ConnectionException
        full_data: dict = handle_response(response).get('data')
        symbol_ticker: dict = full_data.get(CrosstowerConfig.DEFAULT_SYMBOL)
        if not symbol_ticker:
            return None
        return Ticker(symbol_ticker)

    def stop(self) -> None:
        self.connection.close()
    