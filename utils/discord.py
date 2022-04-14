import requests
import json
from utils import Logger
from utils.environment import env

class DiscordWebhook:

    def __init__(self, app_name: str):
        self.log = Logger.setup(app_name)
        self.name = app_name
        self.alert_url = env.discord_alert_webhook
        self.status_url = env.discord_status_webhook
        if not self.alert_url:
            self.log.error(f'No discord webhook url found in env variables')
            raise Exception(f'No discord webhook url found in env variables')

    def send_alert(self, message: str):
            payload = {"username": self.name, "content": message}
            self.log.debug(f'Sending discord alert: {message}')
            _ = requests.post(self.alert_url, data=payload)

    def send_status(self, message: str):
        payload = {"username": self.name, "content": message}
        self.log.debug(f'Sending discord status: {message}')
        _ = requests.post(self.status_url, data=payload)