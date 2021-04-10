from requests import get
from time import strptime, struct_time

class Symbol:
    """Return the actual list of currency symbols (currency pairs) traded on exchange. 
    The first listed currency of a symbol is called the base currency, and the second currency is called the quote currency. 
    The currency pair indicates how much of the quote currency is needed to purchase one unit of the base currency.
    """

    def __init__(self, symbol) -> None:
        """
        `GET /api/2/public/symbol/{symbol}`

        Data for a certain symbol. Requires no API key Access Rights.
        """
        resp = get(f"https://api.crosstower.com/api/2/public/symbol/{symbol}")
        if resp.status_code != 200:
            raise Exception("Invalid symbol or bad connection.")
        self._data = resp.json()

    def refresh(self):
        self.__init__(self.id)

    @property
    def id(self) -> str:
        """Symbol (currency pair) identifier, for example, 'ETHBTC'"""
        return self._data.get('id')

    @property
    def base_currency(self) -> str:
        """Name of base currency"""
        return self._data.get('baseCurrency')

    @property
    def base_currency(self) -> str:
        """Name of quote currency"""
        return self._data.get('quoteCurrency')

    @property
    def quantity_increment(self) -> float:
        """Symbol quantity should be divided by this value with no remainder"""
        return float(self._data.get('quantityIncrement'))

    @property
    def tick_size(self) -> float:
        """Symbol price should be divided by this value with no remainder"""
        return float(self._data.get('tickSize'))

    @property
    def take_liquidity_rate(self) -> float:
        """Default fee rate"""
        return float(self._data.get('takeLiquidityRate'))

    @property
    def provide_liquidity_rate(self) -> float:
        """Default fee rate for market making trades"""
        return float(self._data.get('provideLiquidityRate'))

    @property
    def fee_currency(self) -> float:
        """Value of charged fee"""
        return float(self._data.get('feeCurrency'))

    @property
    def margin_trading(self) -> bool:
        """Is margin trading available. Optional parameter"""
        return self._data.get('marginTrading')

    @property
    def max_initial_leverage(self) -> float:
        """Maximum leverage that user can use for margin trading. Optional parameter"""
        return self._data.get('maxInitialLeverage')


class Ticker:
    """Symbol ticker information"""

    def __init__(self, symbol: str) -> None:
        """
        `GET /api/2/public/ticker/{symbol}`

        Ticker for a certain symbol. Requires no API key Access Rights.
        """
        resp = get(f"https://api.crosstower.com/api/2/public/ticker/{symbol}")
        if resp.status_code != 200:
            raise Exception("Invalid symbol or bad connection.")
        self._data = resp.json()

    def refresh(self):
        self.__init__()

    @property
    def symbol(self) -> str:
        """Symbol name"""
        return self._data.get('symbol')

    @property
    def ask(self) -> float:
        """Best ask price. Can return 'None' if no data."""
        return float(self._data.get('ask'))

    @property
    def bid(self) -> float:
        """Best bid price. Can return 'None' if no data."""
        return float(self._data.get('bid'))

    @property
    def last(self) -> float:
        """Last trade price. Can return 'None' if no data."""
        return self._data.get('last')

    @property
    def open(self) -> float:
        """Last trade price 24 hours ago. Can return 'None' if no data."""
        return self._data.get('open')

    @property
    def low(self) -> float:
        """Lowest trade price within 24 hours"""
        return self._data.get('low')

    @property
    def high(self) -> float:
        """Highest trade price within 24 hours"""
        return self._data.get('high')

    @property
    def volume(self) -> float:
        """Total trading amount within 24 hours in base currency"""
        return self._data.get('volume')

    @property
    def volume_quote(self) -> float:
        """Total trading amount within 24 hours in quote currency"""
        return self._data.get('volume_quote')

    @property
    def timestamp(self) -> struct_time:
        """Last update or refresh ticker timestamp"""
        return strptime(
            self._data.get('timestamp'),
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )


