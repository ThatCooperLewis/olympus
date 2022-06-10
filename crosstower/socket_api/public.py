import asyncio
import json
from time import time as now

from utils.config import DEFAULT_SYMBOL, SOCKET_V3_URL
from websocket import create_connection, WebSocket


class TickerWebsocket:

    def __init__(self, symbol: str = DEFAULT_SYMBOL) -> None:
        self.symbol = symbol
        self.uri = SOCKET_V3_URL + '/public'
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

    def get_ticker(self) -> str:
        '''
        Synchronously retrieves ticker data from the queue.
        '''
        return self.connection.recv()

    def stop(self) -> None:
        self.connection.close()
    