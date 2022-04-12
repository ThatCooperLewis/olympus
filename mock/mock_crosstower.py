from crosstower.socket_api.private import OrderListener
import json
from typing import List

from crosstower.models import Balance, Order
from crosstower.rest_api import MarketData
from utils.config import CRYPTO_SYMBOL, FIAT_SYMBOL
from websockets import connect as Connection

# TODO: Add logger, zero-balance logic
'''
POSTGRES TODO

this needs a lot of work

Hermes is sending Order objects here & asking for balances

Postgres needs new methods:
    1. mock order submission needs its own query? includes other columns
    2. mock trading balance - get latest balance from mock orders table e.g. "ending_btc_balance"

Pretty sure MockBalanceSheet can be ditched

Gotta create Postgres instance to share across classes, with the overridden table names
'''


class MockBalanceSheet:

    '''
    Used to read/write the balances from a file. Pass this between mock classes to keep things consistent
    '''

    def __init__(self, filepath: str):
        if type(filepath) is not str:
            raise Exception("Invalid type for balance sheet filepath: expected str")
        self.file_path = filepath
        self.reload()

    def save(self):
        with open(self.file_path, 'w+') as file:
            json.dump(self.__balances, file)

    @property
    def balances(self) -> List[Balance]:
        # print("[BalanceSheet]: Fetching all balances")
        converted = []
        for balance_dict in self.__balances:
            converted.append(Balance(balance_dict))
        return converted

    def reload(self):
        with open(self.file_path, 'r') as file:
            self.__balances = json.load(file)
            if type(self.__balances) is not list:
                raise Exception(
                    "[BalanceSheet]: Invalid JSON format: expected list")

    def set_balance(self, currency: str, amount_change: float):
        # print(
        #     f"[BalanceSheet]: Adjusting balance of {currency} by amount {amount_change}")
        for i, balance_dict in enumerate(self.__balances):
            if balance_dict.get('currency') == currency:
                self.__balances[i]['available'] += amount_change
                self.save()
                return
        raise Exception(f"Currency {currency} not found in balance sheet")


class MockSocket:

    '''
    Used to execute mock orders. Makes changes to a MockBalanceSheet object based on order data & current BTC price. 
    Conforms to `crosstower.socket_api.SocketAPI`
    '''

    def __init__(self, balances: MockBalanceSheet) -> None:
        self.balance_sheet = balances
        # print("[MockSocket]: Initialized!")
        # print(self.balance_sheet)
        return

    async def request(self, socket: Connection, method: str, params: dict):
        # print("[MockSocket]: New request incoming...")
        if method != 'newOrder':
            raise NotImplementedError
        # TODO: Get latest price from ticker feed table in postgres, prevent API failures
        ticker = MarketData.get_ticker()
        latest_price = ticker.ask
        side = params['side']
        btc_quantity: float = float(params['quantity'])
        usd_quantity = btc_quantity * latest_price
        if side == 'buy':
            # print("[MockSocket]: It's a buy order")
            usd_quantity *= -1
        elif side == 'sell':
            # print("[MockSocket]: It's a sell order")
            btc_quantity *= -1
        else:
            raise Exception(
                "Unrecognized order type, expected 'buy' or 'sell'")

        self.balance_sheet.set_balance(FIAT_SYMBOL, usd_quantity)
        self.balance_sheet.set_balance(CRYPTO_SYMBOL, btc_quantity)
        # print("[MockSocket]: Balances updated!")
        
        # TODO:
        # self.postgres.insert_mock_order(params)
        
        return True

    async def get_authenticated_socket(self):
        return None


class MockTrading:

    def __init__(self, balances: MockBalanceSheet) -> None:
        self.balance_sheet = balances
        # print("MockTrading initialized")
        # print(self.balance_sheet)

    def get_trading_balance(self, currencies: list = []):
        # TODO:
        # self.postgres.get_mock_trading_balances()
        # Figure out how to index the two returned values properly        
        return self.balance_sheet.balances


class MockAPI:

    '''
    Barebones mock class for mocking account balance and trade orders
    As of 9.7.2021, this is equipped to override the necessary params for Hermes 
    '''

    def __init__(self, balance_sheet_path: str, mock_discord) -> None:
        self.__balance_sheet = MockBalanceSheet(balance_sheet_path)
        self.trading = MockTrading(self.__balance_sheet)
        self.listener = OrderListener(websocket_override=MockSocket(self.__balance_sheet))
        self.listener.discord = mock_discord
        return
