from sys import api_version
from time import strptime, struct_time
from typing import List


class Trade:
    """Trades information for a symbol"""

    def __init__(self, data: dict) -> None:
        self._data = data

    @property
    def dict(self) -> dict:
        return self._data

    @property
    def id(self) -> int:
        """Trade identifier"""
        return int(self._data.get('id'))
    
    @property
    def price(self) -> float:
        """Trade price"""
        return float(self._data.get('price'))

    @property
    def quantity(self) -> float:
        """Trade quantity"""
        return float(self._data.get('quantity'))

    @property
    def side(self) -> str:
        """Trade side, `"sell"` or `"buy"`"""
        return self._data.get('side')

    @property
    def timestamp(self) -> struct_time:
        """Trade timestamp"""
        return strptime(
            self._data.get('timestamp'),
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )


class Order:

    def __init__(self, data: dict) -> None:
        self._data = data

    @property
    def dict(self) -> dict:
        return self._data

    @property
    def id(self) -> int:
        """Order unique identifier as assigned by exchange"""
        return int(self._data.get('id'))

    @property
    def client_order_id(self) -> str:
        """
        Order unique identifier as assigned by trader. 
        
        Uniqueness must be guaranteed within a single trading day, including all active orders.
        """
        return self._data.get('clientOrderId')

    @property
    def symbol(self) -> str:
        """Trading symbol name, ex. `"ETHBTC"`"""
        return self._data.get('symbol')

    @property
    def side(self) -> str:
        """Trade side, `"sell"` or `"buy"`"""
        return self._data.get('side')

    @property
    def status(self) -> str:
        """
        Order state

        Possible values: `new`, `suspended`, `partiallyFilled`, `filled`, `canceled`, `expired`
        """
        return self._data.get('status')

    @property
    def type(self) -> str:
        """Possible values: `limit`, `market`, `stopLimit`, and `stopMarket`"""
        return self._data.get('type')

    @property
    def timeInForce(self) -> str:
        """
        Time in Force is a special instruction used when placing a trade to indicate how long an order will remain active before it is executed or expired.
        
        `GTC` - ''Good-Till-Cancelled'' order won't be closed until it is filled.
        
        `IOC` - ''Immediate-Or-Cancel'' order must be executed immediately. Any part of an IOC order that cannot be filled immediately will be cancelled.
        
        `FOK` - ''Fill-Or-Kill'' is a type of ''Time in Force'' designation used in securities trading that instructs a brokerage to execute a transaction immediately and completely or not execute it at all.
        
        `Day` - keeps the order active until the end of the trading day (UTC).
        
        `GTD` - ''Good-Till-Date''. The date is specified in expireTime.
        """
        return self._data.get('type')
    
    @property
    def quantity(self) -> float:
        """Order quantity"""
        return float(self._data.get('quantity'))
    
    @property
    def price(self) -> float:
        """Order price"""
        return float(self._data.get('price'))

    @property
    def avg_price(self) -> float:
        """Average execution price, only for history orders"""
        return float(self._data.get('avgPrice'))
    
    @property
    def cum_quantity(self) -> float:
        """Average execution price, only for history orders"""
        return float(self._data.get('cumQuantity'))

    @property
    def created_at(self) -> struct_time:
        """Order creation date"""
        return strptime(
            self._data.get('createdAt'),
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

    @property
    def updated_at(self) -> struct_time:
        """Date of order's last update"""
        return strptime(
            self._data.get('updatedAt'),
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

    @property
    def stop_price(self) -> float:
        """Required for stop-limit and stop-market orders"""
        return float(self._data.get('stopPrice'))
    
    @property
    def post_only(self) -> bool:
        """
        A post-only order is an order that does not remove liquidity. 
        If your post-only order causes a match with a pre-existing order as a taker, then the order will be cancelled.
        """
        if str(self._data.get('postOnly')).lower() in 'true':
            return True
        return False

    @property
    def expire_time(self) -> struct_time:
        """Date of order expiration for `timeInForce = GTD`"""
        return strptime(
            self._data.get('expireTime'),
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

    @property
    def trades_report(self) -> List[Trade]:
        return


class Symbol:
    """
    The currency pair indicates how much of the quote currency is needed to purchase one unit of the base currency. 
    The first listed currency of a symbol is called the base currency, and the second currency is called the quote currency. 
    """

    def __init__(self, data: dict) -> None:
        self._data = data

    @property
    def dict(self) -> dict:
        return self._data

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

    def __init__(self, data: dict) -> None:
        self._data = data

    @property
    def dict(self) -> dict:
        return self._data

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


class Candle:
    """Candles are used for the representation of a specific symbol as an OHLC chart."""

    def __init__(self, data: dict) -> None:
        self._data = data

    @property
    def dict(self) -> dict:
        return self._data

    @property
    def open(self) -> float:
        """Opening price"""
        return float(self._data.get('open'))

    @property
    def close(self) -> float:
        """Closing price"""
        return float(self._data.get('close'))

    @property
    def min(self) -> float:
        """Lowest price for the period"""
        return float(self._data.get('min'))

    @property
    def max(self) -> float:
        """Highest price for the period"""
        return float(self._data.get('max'))

    @property
    def volume(self) -> float:
        """Volume in base currency"""
        return float(self._data.get('volume'))

    @property
    def volume_quote(self) -> float:
        """Volume in quote currency"""
        return float(self._data.get('volumeQuote'))


class Balance:
    """ User's trading balance for a specific coin """

    def __init__(self, data: dict) -> None:
        self._data = data

    @property
    def dict(self) -> dict:
        return self._data

    @property
    def currency(self) -> str:
        """Currency code"""
        return self._data.get('currency')
    
    @property
    def available(self) -> float:
        """Amount available for trading or transfer to main account"""
        return float(self._data.get('available'))

    @property
    def reserved(self) -> float:
        """Amount reserved for active orders or incomplete transfers to main account"""
        return float(self._data.get('reserved'))


class Commission:
    """Personal trading commission rate"""

    def __init__(self, data: dict, symbol: str = '') -> None:
        self._data = data
        self._data['symbol'] = symbol

    @property
    def dict(self) -> dict:
        return self._data

    @property
    def symbol(self) -> str:
        return self._data.get('symbol')

    @property
    def taker_rate(self) -> float:
        """takeLiquidityRate"""
        return self._data.get('takeLiquidityRate')

    @property
    def maker_rate(self) -> float:
        """provideLiquidityRate"""
        return self._data.get('provideLiquidityRate')