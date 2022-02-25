import hashlib
import hmac
import json
import time
from base64 import b64encode
from typing import Tuple
from urllib.parse import urlparse

import requests
from requests.auth import AuthBase

import crosstower.utils as utils
from utils.config import REST_URL


class __HS256__(AuthBase):

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __call__(self, r):
        url = urlparse(r.url)
        timestamp = str(int(time.time()))
        msg = r.method + timestamp + url.path
        if url.query != "":
            msg += "?" + url.query
        if r.body:
            msg += r.body

        signature = hmac.new(self.password.encode(),
                             msg.encode(), hashlib.sha256).hexdigest()
        authstr = "HS256 " + b64encode(
            b':'.join((self.username.encode(), timestamp.encode(), signature.encode()))).decode().strip()

        r.headers['Authorization'] = authstr
        return r


class __BasicAuth__:

    def __init__(self, api_key: str, secret_key: str) -> None:
        self.__set_auth_header(api_key, secret_key)

    def __set_auth_header(self, api_key: str, secret_key: str):
        try:
            credential_bytes = f"{api_key}:{secret_key}".encode('ascii')
            credential_base64 = b64encode(credential_bytes)
            credentials = credential_base64.decode('ascii')
            if not credentials:
                raise Exception('Failed to encode REST authentication header')
            self.auth_header = {'Authorization': f'Basic {credentials}'}
        except:
            raise Exception("Credentials file missing or invalid")

    def _auth_get(self, endpoint: str, request_name: str = 'API') -> dict:
        url = utils.build_url(endpoint)
        resp = requests.get(
            url=url,
            headers=self.auth_header
        )
        return utils.handle_response(resp, request_name)

    def _auth_put(self, endpoint: str, request_name: str = 'API', query_params: dict = {}) -> dict:
        url = utils.build_url(endpoint)
        resp = requests.put(
            url=url,
            headers=self.auth_header,
            data=query_params
        )
        return utils.handle_response(resp, request_name)

    def _auth_delete(self, endpoint: str, request_name: str = 'API') -> dict:
        url = utils.build_url(endpoint)
        resp = requests.delete(
            url=url,
            headers=self.auth_header
        )
        return utils.handle_response(resp, request_name)


class __HS256Auth__:

    def __init__(self, api_key: str, secret_key: str) -> None:
        self.session = requests.session()
        self.session.auth = __HS256__(api_key, secret_key)

    def _auth_get(self, endpoint: str, request_name: str = 'API') -> dict:
        url = utils.build_url(endpoint)
        resp = self.session.get(url)
        return utils.handle_response(resp, request_name)

    def _auth_put(self, endpoint: str, request_name: str = 'API', query_params: dict = {}) -> dict:
        url = utils.build_url(endpoint)
        resp = self.session.put(
            url=url, 
            headers=self.auth_header, 
            data=query_params
        )
        return utils.handle_response(resp, request_name)

    def _auth_delete(self, endpoint: str, request_name: str = 'API') -> dict:
        url = utils.build_url(endpoint)
        resp = self.session.delete(
            url=url,
            headers=self.auth_header
        )
        return utils.handle_response(resp, request_name)


class Authentication:

    def __init__(self, method: str = 'basic', path='credentials.json') -> None:
        key, secret = self.__load(path)
        if method.lower() == 'basic':
            api = __BasicAuth__(key, secret)
        elif method.lower() == 'hs256':
            api = __HS256Auth__(key, secret)
        else:
            err = 'Invalid `auth_method` param, use either "basic" or "hs256"'
            raise Exception(err)
        self.auth_get = api._auth_get
        self.auth_put = api._auth_put
        self.auth_delete = api._auth_delete
        self.__authenticate()
        
    def __authenticate(self) -> list:
        return self.auth_get('trading/balance')

    def __load(self, path: str) -> Tuple[str, str]:
        try:
            with open(path, 'r') as file:
                creds = json.load(file)
            user = creds.get('api_key')
            pw = creds.get('secret_key')
            if not (user and pw):
                err = "Could not find 'api_key' and 'secret_key' in credentials"
                raise Exception(err)
            return user, pw
        except:
            raise Exception("Credentials file missing or invalid")

    def auth_get(self, endpoint: str, request_name: str = 'API') -> dict:
        raise NotImplementedError

    def auth_put(self, endpoint: str, request_name: str = 'API', query_params: dict = {}) -> dict:
        raise NotImplementedError

    def auth_delete(self, endpoint: str, request_name: str = 'API') -> dict:
        raise NotImplementedError
