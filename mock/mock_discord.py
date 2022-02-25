from utils import Logger
import json

# TODO: Move config to a config file
CREDENTIALS_FILE = 'credentials.json'

class MockDiscord:

    def __init__(self, app_name: str):
        self.log = Logger.setup(self.__class__.__name__)
        self.name = app_name
        # Raise an exception if no url is found in the credentials file
        if not self.__get_webhook_url_from_json_file(CREDENTIALS_FILE):
            raise Exception(f'No discord webhook url found in {CREDENTIALS_FILE}')

    def send_alert(self, message: str):
        self.log.info(f"{self.name}: {message}")

    def __get_webhook_url_from_json_file(self, file_path: str):
        with open(file_path) as json_file:
            data: dict = json.load(json_file)
            return data.get("discord_webhook")