import base64
import json
import requests
from time import sleep, strptime, time
from calendar import timegm


class CrossTower:

    def __init__(self):
        self.auth_header = self.__load_credentials()
        self.__authenticate()

    def __load_credentials(self):
        creds = None
        try:
            with open('credentials.json', 'r') as file:
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
            return {'Authorization': f'Basic {credentials}'}
        except:
            raise Exception("Credentials file missing or invalid")

    def __authenticate(self) -> list:
        resp = requests.get(
            'https://api.crosstower.com/api/2/trading/balance', headers=self.auth_header)
        if resp.status_code != 200:
            raise Exception(
                f'Unexpected auth response code: {resp.status_code}')
        return resp.json()

    def __market_order(self, type: str, amount_btc: float) -> dict:
        if type not in ['buy','sell']:
            raise Exception("Bad 'type' arg for __market_order")
        timestamp = int(time())
        resp = requests.put(
            f"https://api.crosstower.com/api/2/order/{timestamp}", 
            headers=self.auth_header,
            data={
                'symbol' : 'BTCUSD_TR',
                'side' : 'buy',
                'type' : 'market',
                'quantity': amount_btc
            }
        )
        return resp.json()

    def buy_btc(self, amount_btc: float):
        return self.__market_order('buy', amount_btc)

    def sell_btc(self, amount_btc: float):
        return self.__market_order('sell', amount_btc)
    
    def get_balance(self, currencies: list = ['USD', 'BTC']):
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
    def get_ticker(cls):
        resp = requests.get(
            "https://api.crosstower.com/api/2/public/ticker/BTCUSD_TR")
        return resp.json()




def scrape_tickers():
    print("Starting...")
    while True:
        try:
            ticker = CrossTower.get_ticker()
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
    ct = CrossTower()
    print(ct.buy_btc(0.00017206))
    # pass
    # scrape_tickers()