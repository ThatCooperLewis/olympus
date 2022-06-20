import asyncio
import json
from queue import Queue
from threading import Thread
from time import sleep
from time import time as now
from typing import List
import traceback
from collections.abc import Callable

from crosstower.models import Balance, Order
from crosstower.socket_api import utils
from websockets import connect as Connection

from utils import Logger, DiscordWebhook
from utils.config import CrosstowerConfig
from utils.environment import env

class SocketAPI:

    def __init__(self):
        return

    @classmethod
    async def request(cls, socket: Connection, method: str, params: dict, uuid: str = None):
        data = {
            "method": method,
            "params": params,
            "id": int(now())
        }
        await socket.send(json.dumps(data))
        response = await socket.recv()
        return utils.handle_response(response).get('result')

    @classmethod
    async def get_authenticated_socket(cls) -> Connection:
        public_key = env.crosstower_api_key
        secret_key = env.crosstower_secret_key
        if not public_key or not secret_key:
            raise Exception("Couldn't retrieve api & secret key.")
        websocket = await Connection(CrosstowerConfig.SOCKET_V3_URL + '/trading')
        data = {
            "type": "BASIC",
            "api_key": public_key,
            "secret_key": secret_key
        }
        await cls.request(websocket, 'login', data)
        return websocket


class Trading:

    def __init__(self, symbol: str = CrosstowerConfig.DEFAULT_SYMBOL):
        self.symbol = symbol
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.websocket: Connection = loop.run_until_complete(
            SocketAPI.get_authenticated_socket()
        )

    def __request_until_complete(self, method: str, params: str):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            if str(e).startswith('There is no current event loop in thread'):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            else:
                raise
        try:
            return loop.run_until_complete(SocketAPI.request(self.websocket, method, params))
        except Exception as e:
            print(traceback.format_exc())
            raise

    def get_active_orders(self) -> List[Order]:
        """
        `getOrders`

        Requires the "Place/cancel orders" API key Access Right.

        Returns
        ---------
        List of active `Order` objects
        """
        orders_list = self.__request_until_complete('spot_get_orders', {})
        orders = []
        for order_data in orders_list:
            orders.append(Order(order_data))
        return orders

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
        result = []
        for i in range(3):
            try:
                result = self.__request_until_complete('spot_balances', {})
                break
            except:
                continue
        if not result:
            return []
        balance = []
        count = len(currencies)
        for coin in result:
            if count == 0:
                balance.append(Balance(coin))
            elif coin['currency'] in currencies:
                balance.append(Balance(coin))
        return balance

    def cancel_order(self, order: Order) -> Order:
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
        params = { 'client_order_id': order.client_order_id }
        return Order(self.__request_until_complete('spot_cancel_order', params))

    def place_new_order(self, order: Order) -> Order:
        order = self.__request_until_complete('spot_new_order', order.dict)
        return Order(order)

    """ Orders Threading """

class OrderListener:

    def __init__(self, websocket_override=None) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.__socket: SocketAPI = SocketAPI
        if websocket_override:
            self.__socket = websocket_override 
        self.__thread: Thread = Thread(target=self.__wait_loop, daemon=True)
        self.__queue: Queue = Queue()
        self.__quit = False

    async def __orders_coroutine(self):
        try:
            socket = await self.__socket.get_authenticated_socket()
            while not self.__quit:
                if self.__queue.qsize() > 0:
                    order_object: OrderListenerObject = self.__queue.get()
                    order_object.on_submission()
                    await self.__socket.request(socket, 'spot_new_order', order_object.order.dict, order_object.order.uuid)
                    order_object.on_complete()
                sleep(0.1)
            self.log.debug('self.__orders_coroutine() is quitting')
        except KeyboardInterrupt:
            self.log.debug('KeyboardInterrupt during orders coroutine')
            pass
        except Exception as e:
            self.log.error(f'Exception in order executor coroutine: {traceback.format_exc()}')
            self.discord.send_alert(f'Exception in order executor coroutine: {traceback.format_exc()}')
            pass

    def __wait_loop(self):
        try:
            self.log.debug('Starting order listener')
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            future = asyncio.ensure_future(self.__orders_coroutine())
            loop.run_until_complete(future)
        except KeyboardInterrupt:
            self.__quit = True
        except Exception:
            self.log.error(f'Exception in order __wait_loop: {traceback.format_exc()}')
            self.discord.send_alert(f'Exception in order __wait_loop: {traceback.format_exc()}')
        finally:
            self.log.debug('Closing')
            loop.close()

    def submit_order(self, order: Order, on_submission: Callable[[Order], None], on_complete: Callable[[Order], None]):
        """Put `Order` in queue for execution"""
        order_object = OrderListenerObject(order, on_submission, on_complete)
        self.__queue.put(order_object)

    # Make the whole class behave like a thread

    def start(self):
        self.__thread.start()

    def end(self):
        self.__quit = True

    def join(self, timeout: int =None):
        self.__quit = True
        self.__thread.join(timeout=timeout)

    def is_alive(self):
        return self.__thread.is_alive()


class OrderListenerObject:
    
    def __init__(self, order: Order, on_submission: Callable[[Order], None] = None, on_complete: Callable[[Order], None] = None):
        '''Container for Order object, along with callbacks for submission (before API response) and completion (after API response)'''
        self.order = order
        self.__on_submission: Callable[[Order], None] = on_submission
        self.__on_complete: Callable[[Order], None] = on_complete
        
    def on_submission(self):
        if self.__on_submission:
            self.__on_submission(self.order)
        
    def on_complete(self):
        if self.on_complete:
            self.__on_complete(self.order)