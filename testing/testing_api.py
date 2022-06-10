from crosstower.socket_api.private import OrderListener
import json
from typing import List

from crosstower.models import Balance
from utils.config import CRYPTO_SYMBOL, FIAT_SYMBOL 
from websockets import connect as Connection
from requests import get

class FakeBalanceSheet:

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
        for i, balance_dict in enumerate(self.__balances):
            if balance_dict.get('currency') == currency:
                self.__balances[i]['available'] += amount_change
                self.save()
                return
        raise Exception(f"Currency {currency} not found in balance sheet")


class FakeSocket:

    '''
    Used to execute mock orders. Makes changes to a FakeBalanceSheet object based on order data & current BTC price. 
    Conforms to `crosstower.socket_api.SocketAPI`
    '''

    def __init__(self, balances: FakeBalanceSheet) -> None:
        self.balance_sheet = balances
        return

    async def request(self, socket: Connection, method: str, params: dict, uuid: str = None):
        if method != 'newOrder':
            raise NotImplementedError
        resp = get(f"https://api.crosstower.com/api/2/public/ticker/BTCUSD")
        latest_price = float(resp.json()['ask'])
        side = params['side']
        btc_quantity: float = float(params['quantity'])
        usd_quantity = btc_quantity * latest_price
        if side == 'buy':
            usd_quantity *= -1
        elif side == 'sell':
            btc_quantity *= -1
        else:
            raise Exception(
                "Unrecognized order type, expected 'buy' or 'sell'")

        self.balance_sheet.set_balance(FIAT_SYMBOL, usd_quantity)
        self.balance_sheet.set_balance(CRYPTO_SYMBOL, btc_quantity)
        return True

    async def get_authenticated_socket(self):
        return None


class FakeTrading:

    def __init__(self, balances: FakeBalanceSheet) -> None:
        self.balance_sheet = balances

    def get_trading_balance(self, currencies: list = []):
        return self.balance_sheet.balances


class TestingAPI:

    def __init__(self, balance_sheet_path: str, mock_discord) -> None:
        self.__balance_sheet = FakeBalanceSheet(balance_sheet_path)
        self.trading = FakeTrading(self.__balance_sheet)
        self.listener = OrderListener(websocket_override=FakeSocket(self.__balance_sheet))
        self.listener.discord = mock_discord
        return