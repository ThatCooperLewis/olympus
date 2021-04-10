import base64
import json
import requests
from calendar import timegm
from time import sleep, strptime, time
from objects import Symbol, Ticker

SYMBOL = 'BTCUSD_TR'

class API:

    def __init__(self, credentials_path='credentials.json'):
        self.__load_credentials(credentials_path)
        self.__authenticate()

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

    def __authenticate(self) -> list:
        resp = requests.get(
            'https://api.crosstower.com/api/2/trading/balance',
            headers=self.auth_header
        )
        if resp.status_code != 200:
            error_str = f'Unexpected auth response code: {resp.status_code}'
            raise Exception(error_str)
        return resp.json()

    def __market_order(self, side: str, amount: float, symbol: str, ) -> dict:
        if amount < 0.00001:
            raise Exception('Intended BTC purchase is too small')
        if side not in ['buy', 'sell']:
            raise Exception("Bad 'side' arg for __market_order")
        timestamp = int(time())
        resp = requests.put(
            f"https://api.crosstower.com/api/2/order/{timestamp}",
            headers=self.auth_header,
            data={
                'symbol': 'BTCUSD_TR',
                'side': side,
                'type': 'market',
                'quantity': amount
            }
        )
        if resp.status_code != 200:
            print('ERROR: Bad response code from market order')
            print(resp.content)
            return None
        return resp.json()

    def buy(self, amount: float, symbol: str = 'BTCUSD_TR') -> dict:
        return self.__market_order('buy', amount, symbol)

    def sell(self, amount: float, symbol: str = 'BTCUSD_TR') -> dict:
        return self.__market_order('sell', amount, symbol)

    def fee_rate(self) -> dict:
        resp = requests.get(
            "https://api.crosstower.com/api/2/trading/fee/BTCUSD_TR",
            headers=self.auth_header
        )
        return resp.json()

    def balance(self, currencies: list = ['USD', 'BTC']) -> dict:
        result = self.__authenticate()
        balance = {}
        for coin in result:
            if coin['currency'] in currencies:
                balance[coin['currency']] = {
                    'available': coin['available'],
                    'reserved': coin['reserved']
                }
        return balance

    @classmethod
    def get_order_book(cls):
        pass

    @classmethod
    def get_symbol(cls, symbol: str = 'BTCUSD_TR') -> requests.Response:
        return Symbol(symbol)

    @classmethod
    def get_ticker(cls, symbol: str = 'BTCUSD_TR') -> requests.Response:
        return Ticker(symbol)

def scrape_tickers():
    print("Starting...")
    while True:
        try:
            ticker = API.ticker().json()
            if not ticker.get('ask'):
                print("ERROR: Got bad ticker\n")
                print(ticker)
                continue
            with open("crosstower.csv", "a") as file:
                print('Opening file...', end='\r')
                utc_time = strptime(
                    ticker.get('timestamp'),
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                line = f"{ticker.get('ask')},{ticker.get('bid')},{ticker.get('last')},{ticker.get('low')},{ticker.get('high')},{ticker.get('open')},{ticker.get('volume')},{ticker.get('volumeQuote')},{timegm(utc_time)}\n"
                print('Writing line...', end='\r')
                file.write(line)
                file.close()
            print('Waiting (1/4)  ', end='\r')
            sleep(15)
            print('Waiting (2/4)  ', end='\r')
            sleep(15)
            print('Waiting (3/4)  ', end='\r')
            sleep(15)
            print('Waiting (4/4)  ', end='\r')
            sleep(15)
        except Exception as err:
            print("Uh oh! Didn't work\n")
            print(err)
            continue


if __name__ == "__main__":
    ct = API()
    # print(ct.get_btc_symbol())
    # print(ct.buy_btc(0.0001))
    sm = Symbol('ETHBTC')
    sm.margin_trading
    print(sm.base_currency)
    # pass
    # scrape_tickers()