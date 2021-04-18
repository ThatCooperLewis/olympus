from calendar import c, timegm
from time import sleep, strptime
import asyncio

import requests

from crosstower.rest_api import AccountManagement as Account
from crosstower.rest_api import MarketData as market
from crosstower.rest_api import Trading
from crosstower.socket_api import public

from crosstower.auth import Authentication
def scrape_tickers():
    print("Starting...")
    while True:
        try:
            print("Sending request..", end='\r')
            ticker = requests.get(f"https://api.crosstower.com/api/2/public/ticker/BTCUSD_TR").json()
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
            for i in range(4):
                print(f'Waiting ({i+1}/4)  ', end='\r')
                sleep(15)
        except Exception as err:
            print("Uh oh! Didn't work\n")
            print(err)
            continue


if __name__ == "__main__":
    # trade = Trading()
    # account = Account()
    # print(account.get_account_balance(['BTC', 'USD'])[1].dict)
    # auth = Authentication('hs256')
    # trade = Trading
    # symbol = asyncio.get_event_loop().run_until_complete(public.get_symbol())
    # print(symbol.tick_size)

    public.TickerScraper().run()

    # resp = auth.auth_get('trading/balance')
    # resp = auth.auth_put('order')
    # print(resp)
    # print(account.get_commission())
    # print(market.get_symbol().dict)
    # buy = trade.buy(0.00002)
    # print(buy)
    # print(trade.order_status(493931043903))
    # ct.get
    # sm = Symbol('ETHBTC')
    # sm.margin_trading
    # print(sm.base_currency)
    # pass
    # scrape_tickers()
