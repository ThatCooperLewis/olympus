from time import strptime, struct_time


class Order:

    def __init__(self, data: dict, uuid: str = None) -> None:
        self._data: dict = data
        self.uuid: str = uuid

    @classmethod
    def create(cls, quantity: float, side: str, symbol, order_type: str = 'market', time_in_force: str = 'GTC', price: float = None, stop_price: float = None, uuid: str = None):
        '''
        Create a new order

        Parameters
        ----------
        quantity : float
            Order quantity
        side : str
            Can be `sell` or `buy`
        symbol : str
            Trading symbol, ex. 'BTCUSD'
        order_type : str
            Can be `limit`, `market`, `stopLimit`, `stopMarket`. Defaults to `market`.
        time_in_force : str
            Accepted values: `GTC`, `IOC`, `FOK`, `Day`. Defaults to `GTC`. `GTD` not yet supported.
        price : float
            Order price. Required for `limit` types
        stop_price : float
            Required for `stopLimit` and `stopMarket` orders
        uuid : str
            Internal app use only. Not used by the API.

        Returns
        ----------
        `Order` object
        '''
        bad_args = False
        order_data = {
            'symbol': symbol
        }

        if side in ['sell', 'buy'] and order_type in ['limit', 'market', 'stopLimit', 'stopMarket'] and time_in_force in ['GTC', 'IOC', 'FOK', 'Day']:
            order_data['side'] = side
            order_data['type'] = order_type
        else:
            bad_args = True

        if price:
            if type(price) is float:
                order_data['price'] = str(price)
            else:
                bad_args = True

        if stop_price:
            if type(stop_price) is float:
                order_data['stopPrice'] = str(stop_price)
            else:
                bad_args = True

        if type(quantity) is float:
            order_data['quantity'] = str(quantity)
        else:
            bad_args = True

        if bad_args:
            raise Exception("Bad args passed to Order.create(), check types")
        return Order(order_data, uuid)

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

    @quantity.setter
    def quantity(self, value: float) -> None:
        self._data['quantity'] = float(value)

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


class Ticker:
    """Symbol ticker information"""

    def __init__(self, data: dict) -> None:
        """Symbol ticker information"""
        self._data = data

    @property
    def dict(self) -> dict:
        return self._data

    @property
    def csv_line(self) -> str:
        return f"{self.ask},{self.bid},{self.last},{self.low},{self.high},{self.open},{self.volume},{self.volume_quote},{self.timestamp}\n"

    @property
    def symbol(self) -> str:
        """Symbol name"""
        return self._data.get('symbol')

    @property
    def ask(self) -> float:
        """Best ask price. Can return 'None' if no data."""
        return float(self._data.get('a'))

    @property
    def bid(self) -> float:
        """Best bid price. Can return 'None' if no data."""
        return float(self._data.get('b'))

    @property
    def last(self) -> float:
        """Last trade price. Can return 'None' if no data."""
        return self._data.get('c')

    @property
    def open(self) -> float:
        """Last trade price 24 hours ago. Can return 'None' if no data."""
        return self._data.get('o')

    @property
    def high(self) -> float:
        """Highest trade price within 24 hours"""
        return self._data.get('h')

    @property
    def low(self) -> float:
        """Lowest trade price within 24 hours"""
        return self._data.get('l')

    @property
    def volume(self) -> float:
        """Total trading amount within 24 hours in base currency"""
        return self._data.get('v')

    @property
    def volume_quote(self) -> float:
        """Total trading amount within 24 hours in quote currency"""
        return self._data.get('q')

    @property
    def timestamp(self) -> int:
        """Last update or refresh ticker timestamp"""
        epoch = int(self._data.get('t'))
        if epoch > 2147483647:
            # API wants to send milliseconds sometimes
            # Prevent integer overflow
            epoch = int(epoch/1000)
        return epoch


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
