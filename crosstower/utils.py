from typing import List
from requests import Response

from utils.config import REST_V2_URL
from crosstower.models import Order


def build_url(endpoint: str) -> str:
    if endpoint[0] == '/':
        endpoint = endpoint[1:]
    return f"{REST_V2_URL}/{endpoint}"


def handle_response(response: Response, request_name: str = 'API') -> dict:
    # TODO - Make this an entire class to parse error types
    if response.status_code != 200:
        error_str = f'Unexpected {request_name} response: {response.status_code}'
        print(response.content)
        raise Exception(error_str)
    return response.json()

def aggregate_orders(orders_list) -> List[Order]:
    """Convert a raw dictlist of orders into a list of `Order` objects"""
    orders = []
    for order_data in orders_list:
        orders.append(Order(order_data))
    return orders
