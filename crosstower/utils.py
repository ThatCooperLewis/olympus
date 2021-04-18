from requests import Response
from crosstower.config import REST_URL


def build_url(endpoint: str) -> str:
    if endpoint[0] == '/':
        endpoint = endpoint[1:]
    return f"{REST_URL}/{endpoint}"


def handle_response(response: Response, request_name: str = 'API') -> dict:
    # TODO - Make this an entire class to parse error types
    if response.status_code != 200:
        error_str = f'Unexpected {request_name} response: {response.status_code}'
        print(response.content)
        raise Exception(error_str)
    return response.json()
