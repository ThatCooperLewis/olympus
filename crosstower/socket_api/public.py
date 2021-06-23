import asyncio
import json
from time import time as now

from crosstower.config import DEFAULT_CURRENCY, DEFAULT_SYMBOL, SOCKET_URI
from crosstower.models import Symbol
from crosstower.socket_api import utils
from websockets import connect as Connection


class MarketData:

    def __init__(self) -> None:
        return

    async def request(self, method: str, params: dict):
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


