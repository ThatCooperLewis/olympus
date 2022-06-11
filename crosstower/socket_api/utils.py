import json


def handle_response(response: str) -> dict:
    response = json.loads(response)
    if response.get('error'):
        err = f"API responded with error {response['error']['code']}: '{response['error']['message']}'"
        raise Exception(err)
    return response


