from time import struct_time
from typing import List

from crosstower.config import DEFAULT_SYMBOL, API_BASE_URL
from crosstower.models import Candle, Symbol, Ticker, Trade
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
        sort: str = 'DESC',
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
            Default value: `DESC`
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
        # TODO: Add data here
        if resp.status_code != 200:
            raise Exception("Invalid symbol or bad connection.")
        candle_list = []
        for candle_data in resp.json():
            if not candle_data.get('timestamp'):
                continue
            candle_list.append(Candle(candle_data))
        return candle_list

    @classmethod
    def get_trades(
        cls,
        symbol: str = DEFAULT_SYMBOL,
        sort: str = 'DESC',
        from_date: struct_time = None,
        till_date: struct_time = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Trade]:
        """
        `GET /api/2/public/trades`

        Returns trades for a symbol with a symbol Id. Candles are used for the representation of a specific symbol as an `OHLC` chart.

        Parameters
        ----------
        symbol : str
            Symbol (currency pair) identifier, for example, 'ETHBTC'
        sort : str
            Sort direction
            Accepted values: `ASC`, `DESC`
            Default value: `DESC`
        from_date : datetime
            Interval initial value (optional)
        till_data : datetime
            Interval end value (optional)
        limit : int
            Limit of candles
            Default value: 100
            Max value: 1000
        offset : int
            Default value: 0
            Max value: 100000

        Returns
        ----------
        A list of `Trade` objects with the following properties

        id : str
            Trade identifier
        price : float
            Trade price
        quantity : Float
            Trade quantity
        side : str
            Trade side, `"sell"` or `"buy"`
        timestamp : datetime
            Trade timestamp
        """
        resp = get(
            f"{API_BASE_URL}/public/trades/{symbol}",
            data={
                'symbols': symbol,
                'from': from_date
                # TODO: Fix this
            }
        )
        if resp.status_code != 200:
            raise Exception("Invalid symbol or bad connection.")
        print(resp.json)
        exit()
        trade = []
        for candle_data in resp.json():
            if not candle_data.get('timestamp'):
                continue
            trade.append(Trade(candle_data))
        return trade
    # TODO - Trades, Order Books