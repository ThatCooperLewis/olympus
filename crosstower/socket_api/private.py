import asyncio
import json
from queue import Queue
from threading import Thread
from typing import List

from crosstower.config import DEFAULT_SYMBOL, SOCKET_URI
from crosstower.models import Order, Balance
from crosstower.socket_api import utils
from crosstower.utils import aggregate_orders
from websockets import connect as Connection
from utils import Logger


class SocketAPI:

    def __init__(self):
        return

    @classmethod
    async def request(cls, socket: Connection, method: str, params: dict):
        data = {
            "method": method,
            "params": params,
            "id": 123  # TODO: make good ID generator
        }
        await socket.send(json.dumps(data))
        response = await socket.recv()
        return utils.handle_response(response).get('result')

    @classmethod
    async def get_authenticated_socket(cls, credentials_path: str) -> Connection:
        with open(credentials_path, 'r') as file:
            creds = json.load(file)
            public_key = creds.get('api_key')
            secret_key = creds.get('secret_key')
            if not public_key or not secret_key:
                raise Exception("Couldn't retrieve api & secret key.")
        websocket = await Connection(SOCKET_URI)
        data = {
            "algo": "BASIC",
            "pKey": public_key,
            "sKey": secret_key
        }
        await cls.request(websocket, 'login', data)
        return websocket


class Trading:

    def __init__(self, symbol: str = DEFAULT_SYMBOL, credentials_path: str = 'credentials.json'):
        self.symbol = symbol
        self.credentials_path = credentials_path
        self.websocket: Connection = asyncio.get_event_loop().run_until_complete(
            SocketAPI.get_authenticated_socket(credentials_path)
        )

    def __request_until_complete(self, method: str, params: str):
        return asyncio.get_event_loop().run_until_complete(SocketAPI.request(self.websocket, method, params))

    def get_active_orders(self) -> List[Order]:
        """
        `getOrders`

        Requires the "Place/cancel orders" API key Access Right.

        Returns
        ---------
        List of active `Order` objects
        """
        return aggregate_orders(self.__request_until_complete('getOrders', {}))

    def get_trading_balance(self, currencies: list = []) -> List[Balance]:
        """
        `getTradingBalance`

        Returns the user's trading balance.

        Requires the "Orderbook, History, Trading balance" API key Access Right.

        Parameters
        ----------
        currencies : list
            Optional string array of desired currencies. Output will only contain these currencies.

        Returns
        ----------
        A list of `Balance` objects
        """
        result = self.__request_until_complete('getTradingBalance', {})
        balance = []
        count = len(currencies)
        for coin in result:
            if count == 0:
                balance.append(Balance(coin))
            elif coin['currency'] in currencies:
                balance.append(Balance(coin))
        return balance

    def cancel_order(self, order: Order):
        """
        `cancelOrder`

        Requires the "Place/cancel orders" API key Access Right.

        Parameters
        ----------
        order: Order
            `Order` object with an active order ID

        Returns
        ----------
        Cancelled `Order` object
        """
        params = {'clientOrderId': order.client_order_id}
        result = Order(self.__request_until_complete('cancelOrder', params))

    def place_new_order(self, order: Order) -> Order:
        order = self.__request_until_complete('newOrder', order.dict)
        return Order(order)

    """ Orders Threading """

class OrderListener:

    def __init__(self, credentials_path: str = 'credentials.json', websocket_override=None) -> None:
        self.log = Logger.setup('OrderListener')
        self.__socket: SocketAPI = SocketAPI
        if websocket_override:
            self.__socket = websocket_override 
        self.__thread: Thread = Thread(target=self.__wait_loop, daemon=True)
        self.__queue: Queue = Queue()
        self.__creds_path = credentials_path
        self.__quit = False

    async def __orders_coroutine(self):
        try:
            socket = await self.__socket.get_authenticated_socket(self.__creds_path)
            while not self.__quit:
                if self.__queue.qsize() > 0:
                    order: Order = self.__queue.get()
                    await self.__socket.request(socket, 'newOrder', order.dict)
            self.log.debug('self.__orders_coroutine() is quitting')
        except KeyboardInterrupt:
            self.log.debug('KeyboardInterrupt during orders coroutine')
            pass

    def __wait_loop(self):
        try:
            self.log.debug('Starting order listener')
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.ensure_future(self.__orders_coroutine())
            loop.run_forever()
        except KeyboardInterrupt:
            self.__quit = True
        finally:
            print('Closing')
            loop.close()

    def submit_order(self, order: Order):
        """Put `Order` in queue for execution"""
        self.__queue.put(order)

    def start(self):
        self.__thread.start()

    def end(self):
        self.__quit = True

    def is_running(self):
        return self.__thread.is_alive()
