from time import struct_time
from typing import List

from crosstower.config import DEFAULT_SYMBOL, API_BASE_URL
from crosstower.models import Candle, Symbol, Ticker
from requests import get

# Configure default constants
SYMBOL = 'BTCUSD'


class MarketData:

    def __init__(self) -> None:
        return

    @classmethod
    def get_symbol(cls, symbol: str = DEFAULT_SYMBOL) -> Symbol:
        """
        `GET /api/2/public/symbol/{symbol}`

        Information for a certain currency pair. Requires no API key Access Rights.
        
        The currency pair indicates how much of the quote currency is needed to purchase one unit of the base currency. The first listed currency of a symbol is called the base currency, and the second currency is called the quote currency.

        Parameters
        ----------
        symbol : str
            Symbol (currency pair) identifier, for example, 'ETHBTC'

        Returns
        ----------
        `Symbol` class.
        """
        resp = get(f"{API_BASE_URL}/public/symbol/{symbol}")
        if resp.status_code != 200:
            raise Exception("Invalid symbol or bad connection.")
        data = resp.json()
        return Symbol(data)

    @classmethod
    def get_ticker(cls, symbol: str = DEFAULT_SYMBOL) -> Ticker:
        """
        `GET /api/2/public/ticker/{symbol}`

        Requires no API key Access Rights.

        Parameters
        ----------
        symbol : str
            Symbol (currency pair) identifier, for example, 'ETHBTC'

        Returns
        ----------
        `Ticker` class.
        """
        resp = get(f"{API_BASE_URL}/public/ticker/{symbol}")
        if resp.status_code != 200:
            raise Exception("Invalid symbol or bad connection.")
        data = resp.json()
        return Ticker(data)

    @classmethod
    def get_candles(
        cls,
        symbol: str = DEFAULT_SYMBOL,
        period: str = 'M30',
        sort: str = 'ASC',
        limit: int = 100,
        offset: int = 0,
        from_date: struct_time = None,
        till_date: struct_time = None
    ) -> List[Candle]:
        """
        `GET /api/2/public/candles/{symbol}`

        Returns candles for a certain symbol. Candles are used for the representation of a specific symbol as an `OHLC` chart.

        Parameters
        ----------
        symbol : str
            Symbol (currency pair) identifier, for example, 'ETHBTC'
        period : str
            Accepted values: `M1` (one minute), `M3`, `M5`, `M15`, `M30`, `H1` (one hour), `H4`, `D1` (one day), `D7`, `1M` (one month)
            Default value: `M30` (30 minutes)
        sort : str
            Sort direction
            Accepted values: `ASC`, `DESC`
            Default value: `ASC`
        limit : int
            Limit of candles
            Default value: 100
            Max value: 1000
        offset : int
            Default value: 0
            Max value: 100000
        from : datetime
            Interval initial value (optional)
        till : datetime
            Interval end value (optional)

        Returns
        ----------
        A list of `Candle` classes with the following properties

        timestamp : datetime
            Candle timestamp
        open : Float
            Open price
        close : Float
            Closing price
        min : Float
            Lowest price for the period
        max : Float
            Highest price for the period
        volume : Float
            Volume in base currency
        volumeQuote : Float
            Volume in quote currency
        """
        resp = get(f"{API_BASE_URL}/public/candles/{symbol}")
        if resp.status_code != 200:
            raise Exception("Invalid symbol or bad connection.")
        candle_list = []
        for candle_data in resp.json():
            if not candle_data.get('timestamp'):
                continue
            candle_list.append(Candle(candle_data))
        return candle_list

    # TODO - Trades, Order Books