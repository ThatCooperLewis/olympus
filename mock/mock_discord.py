from utils import Logger
from utils.environment import env


class MockDiscord:

    def __init__(self, app_name: str):
        self.log = Logger.setup(self.__class__.__name__)
        self.name = app_name
        # Raise an exception if no url is found in the credentials file
        if not env.discord_alert_webhook:
            self.log.warn(f'No discord webhook url found in env variables')

    def send_alert(self, message: str):
        self.log.info(f"{self.name}: {message}")
