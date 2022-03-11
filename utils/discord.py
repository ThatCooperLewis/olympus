import requests
import json
from utils import Logger
from utils.config import CREDENTIALS_FILE
import random


class DiscordWebhook:

    def __init__(self, app_name: str):
        self.log = Logger.setup(self.__class__.__name__)
        self.name = app_name
        self.alert_url: str = self.__get_value_from_json_file(CREDENTIALS_FILE)
        self.status_url: str = self.__get_value_from_json_file(CREDENTIALS_FILE, 'discord_status_webhook')
        if not self.alert_url:
            self.log.error(f'No discord webhook url found in {CREDENTIALS_FILE}')
            raise Exception(f'No discord webhook url found in {CREDENTIALS_FILE}')

    def send_alert(self, message: str):
            payload = {"username": self.name, "content": message}
            self.log.debug(f'Sending discord alert: {message}')
            _ = requests.post(self.alert_url, data=payload)

    def send_status(self, message: str):
        payload = {"username": self.name, "content": message}
        self.log.debug(f'Sending discord status: {message}')
        _ = requests.post(self.status_url, data=payload)

    # TODO: Allow for other webhooks for multiple channels

    def __get_value_from_json_file(self, file_path: str, key: str = 'discord_webhook'):
        with open(file_path) as json_file:
            data: dict = json.load(json_file)
            return data.get(key)