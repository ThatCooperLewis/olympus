from calendar import c, timegm
from crosstower.public_api import MarketData as market
from crosstower.private_api import AccountManagement as Account
from crosstower.private_api import Trading
from time import sleep, strptime


from crosstower.models import Balance, Commission
import requests

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
    trade = Trading()
    account = Account()
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
