import base64
import json
from time import time
from typing import List

import requests

from crosstower.config import DEFAULT_SYMBOL, API_BASE_URL
from crosstower.models import Balance, Commission, Order


class __APIAuth:

    def __init__(self, credentials_path='credentials.json'):
        self.__load_credentials(credentials_path)
        self._authenticate()

    def __load_credentials(self, credentials_path):
        try:
            with open(credentials_path, 'r') as file:
                creds = json.load(file)
            api_key = creds.get('api_key')
            secret_key = creds.get('secret_key')
            if not api_key or not secret_key:
                raise Exception
            credential_bytes = f"{api_key}:{secret_key}".encode('ascii')
            credential_base64 = base64.b64encode(credential_bytes)
            credentials = credential_base64.decode('ascii')
            if not credentials:
                raise Exception
            self.auth_header = {'Authorization': f'Basic {credentials}'}
        except:
            raise Exception("Credentials file missing or invalid")

    def _authenticate(self) -> list:
        resp = requests.get(
            f'{API_BASE_URL}/trading/balance',
            headers=self.auth_header
        )
        return self._handle_response(resp, 'Authentication')

    def _handle_response(self, response: requests.Response, request_name: str = 'API'):
        # TODO - Make this an entire class to parse error types
        if response.status_code != 200:
            error_str = f'Unexpected {request_name} response: {response.status_code}'
            print(response.content)
            raise Exception(error_str)
        return response.json()

    def _auth_get(self, endpoint: str, request_name: str = 'API') -> dict:
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        resp = requests.get(
            f"{API_BASE_URL}/{endpoint}",
            headers=self.auth_header
        )
        return self._handle_response(resp, request_name)

    def _auth_put(self, endpoint: str, request_name: str = 'API', query_params: dict = {}) -> dict:
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        resp = requests.put(
            f"{API_BASE_URL}/{endpoint}",
            headers=self.auth_header,
            data=query_params
        )
        return self._handle_response(resp, request_name)

    def _auth_delete(self, endpoint: str, request_name: str = 'API') -> dict:
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        resp = requests.delete(
            f"{API_BASE_URL}/{endpoint}",
            headers=self.auth_header
        )
        return self._handle_response(resp, request_name)


class AccountManagement(__APIAuth):

    def get_account_balance(self, currencies: list = []) -> List[Balance]:
        """
        `GET /api/2/account/balance`

        Returns the user's account balance.

        Requires the "Payment information" API key Access Right.

        Parameters
        ----------
        currencies : list
            Optional string array of desired currencies. Output will only contain these currencies.

        Returns
        ----------
        A list of `Balance` objects
        """
        result = self._auth_get('account/balance', 'Account Balance')
        balance = []
        count = len(currencies)
        for coin in result:
            if count == 0:
                balance.append(Balance(coin))
            elif coin['currency'] in currencies:
                balance.append(Balance(coin))
        return balance


class Trading(__APIAuth):

    def __aggregate_orders(self, orders_list) -> List[Order]:
        """Convert a raw dictlist of orders into a list of `Order` objects"""
        orders = []
        for order_data in orders_list:
            orders.append(Order(order_data))
        return orders

    def __market_order(self, side: str, amount: float, symbol: str = DEFAULT_SYMBOL) -> dict:
        if amount < 0.00001:
            raise Exception('Intended BTC purchase is too small')
        if side not in ['buy', 'sell']:
            raise Exception("Bad 'side' arg for __market_order")
        timestamp = int(time())
        resp = self._auth_put(
            endpoint=f"{API_BASE_URL}/order/{timestamp}",
            request_name='Market Order',
            query_params={
                'symbol': symbol,
                'side': side,
                'type': 'market',
                'quantity': amount
            }
        )
        return self._handle_response(resp, 'Market Order')

    def buy(self, amount: float, symbol: str = DEFAULT_SYMBOL) -> dict:
        return self.__market_order('buy', amount, symbol)

    def sell(self, amount: float, symbol: str = DEFAULT_SYMBOL) -> dict:
        return self.__market_order('sell', amount, symbol)

    def get_trading_balance(self, currencies: list = []) -> List[Balance]:
        """
        `GET /api/2/account/balance`

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
        result = self._auth_get('trading/balance', 'Trading Balance')
        balance = []
        count = len(currencies)
        for coin in result:
            if count == 0: balance.append(Balance(coin))
            elif coin['currency'] in currencies: balance.append(Balance(coin))
        return balance

    def get_trading_commission(self, symbol: str = DEFAULT_SYMBOL) -> Commission:
        """
        `GET /api/2/trading/fee/{symbol}`

        Get personal trading commission rate.

        Requires the "Place/cancel orders" API key Access Right.

        Returns
        ---------
        `Commission` object
        """
        return Commission(self._auth_get(f'trading/fee/{symbol}', 'Commission'), symbol=symbol)

    def get_active_orders(self) -> List[Order]:
        """
        `GET /api/2/order`

        Requires the "Place/cancel orders" API key Access Right.

        Returns
        ---------
        List of active `Order` objects
        """
        return self.__aggregate_orders(self._auth_get('order'))

    def get_active_order(self, order: Order) -> Order:
        """
        GET /api/2/order/{clientOrderId}

        Requires the "Place/cancel orders" API key Access Right.
        """
        return Order(self._auth_get(
            endpoint=f'order/{order.client_order_id}',
            request_name='Get Active Order'
        ))

    def cancel_all_orders(self):
        """
        `DELETE /api/2/order`

        Cancel all active orders, or all active orders for a specified symbol.

        Requires the "Place/cancel orders" API key Access Right.

        Returns
        ---------
        An array of `Order` objects
        """
        return self.__aggregate_orders(self._auth_delete(
            endpoint=f"{API_BASE_URL}/order",
            request_name="Cancel All Orders"
        ))

    def cancel_order(self, order: Order) -> Order:
        """
        `DELETE /api/2/order/{clientOrderId}`

        Requires the "Place/cancel orders" API key Access Right.

        Parameters
        ----------
        order: Order
            `Order` object with an active order ID

        Returns
        ----------
        Cancelled `Order` object
        """
        return Order(self._auth_delete(
            endpoint=f"{API_BASE_URL}/order/{Order.client_order_id}",
            request_name="Cancel Order"
        ))
