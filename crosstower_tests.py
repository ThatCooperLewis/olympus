from calendar import c, timegm
from time import sleep, strptime
import asyncio

import requests

from crosstower.rest_api import AccountManagement as Account
from crosstower.rest_api import MarketData as market
from crosstower.rest_api import Trading 
from crosstower.socket_api import public

from crosstower.auth import Authentication


if __name__ == "__main__":
    # trade = Trading()
    # account = Account()
    # print(account.get_account_balance(['BTC', 'USD'])[1].dict)
    # auth = Authentication('hs256')
    # trade = Trading
    # symbol = asyncio.get_event_loop().run_until_complete(public.get_symbol())
    # print(symbol.tick_size)

    public.TickerScraper().run('crosstower-socket.csv')

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
