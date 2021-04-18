import base64
import json
from time import struct_time, time
from typing import List

import requests

from crosstower.auth import Authentication
from crosstower.config import DEFAULT_SYMBOL, API_BASE_URL
from crosstower.models import Balance, Commission, Order, Address


class __API:

    def __init__(self, auth: Authentication):
        """
        Parameters
        -----------
        auth : Authentication
            Object containing either Basic or HS256 authentication 
        """
        self.api= auth


class AccountManagement(__API):

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
        result = self.api.auth_get('account/balance', 'Account Balance')
        balance = []
        count = len(currencies)
        for coin in result:
            if count == 0:
                balance.append(Balance(coin))
            elif coin['currency'] in currencies:
                balance.append(Balance(coin))
        return balance


    def get_last_deposit_addresses(self, currency) -> list:
        """
        `GET /api/2/account/crypto/addresses/{currency}`
        
        Get last 10 deposit addresses for currency

        Requires the "Payment information" API key Access Right.

        Returns
        ---------
        Address object with the following params
        address : str
            Address for deposit
        paymentId : str
            (Optional) If this field is presented, it is required for deposit
        publicKey : str 
            (Optional) If this field is presented, it is required for deposit
        """
        return self.api.auth_get(f'account/crypto/used-addresses/{currency}')

    def get_last_used_addresses(self, currency) -> list:
        """
        `GET /api/2/account/crypto/used-addresses/{currency}`
        
        Get last 10 unique addresses used for withdraw by currency

        Note: used long ago addresses may be omitted, even if they are among last 10 unique addresses

        Requires the "Payment information" API key Access Right.
        """
        return self.api.auth_get(f'account/crypto/used-addresses/{currency}')

    def withdraw_crypto(
        self,
        currency: str,
        amount: float,
        address: str,
        payment_id: str,
        include_fee: bool = False,
        auto_commit: bool = True,
        public_comment : str = "") -> str:
        """
        Withdraw crypto
        -----------
        `POST /api/2/account/crypto/withdraw`

        Requires the "Withdraw cryptocurrencies" API key Access Right.

        Parameters
        -----------
        currency : str 	
            Currency code
        amount : float
            The amount that will be sent to the specified address
        address : str 
            Address identifier
        payment_id : str 
            Optional parameter
        include_fee : bool 	
            If true is set, then total spent value will include fees.
        auto_commit : bool
            If false is set, then you should commit or rollback transaction in an hour. Used in two phase commit schema.
        public_comment : str 	
            (Optional) Maximum length is 255

        Returns
        ----------
        id : str
            Transaction unique identifier as assigned by exchange
        """
        raise NotImplementedError

    def convert_crypto(self, from_currency: str, to_currency: str, amount: float) -> List[str]:
        """
        Transfer convert between currencies
        ----------
        `POST /api/2/account/crypto/transfer-convert`

        Requires the "Payment information" API key Access Right.

        Parameters
        ----------
        from_currency : str
         	Currency code
        toCurrency : str
            Currency code
        amount : float
            The amount that will be sent to the specified address
        """

    def withdraw_rollback(self, withdraw_id: str) -> bool:
        raise NotImplementedError

    def withdraw_commit(self, withdraw_id: str) -> bool:
        raise NotImplementedError

    def estimate_withdraw_fee(self, currency: str, amount: float) -> float:
        raise NotImplementedError

    def address_is_mine(self, address: str) -> bool:
        raise NotImplementedError

    def bank_transfer(self, currency: str, amount: float, type: str) -> str:
        raise NotImplementedError

    def user_transfer(self, currency: str, amount: float, by: str, identifier: str) -> str:
        raise NotImplementedError

    def get_transaction(self, transaction_id):
        raise NotImplementedError

    def get_transaction_history(
        self,
        currency: str,
        sort: str = 'DESC',
        by: str = 'timestamp',
        from: struct_time = None,
        till: struct_time = None,
        limit: int = 100,
        offset: int = 0,
        showSenders: bool = False) -> dict:
        raise NotImplementedError


class Trading(__API):
    """Create, track, and cancel trade orders"""

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
