from olympus.delphi import Delphi
from utils import DiscordWebhook, Logger

class PredictionEngine:
    
    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.delphi = Delphi()
    
    def run(self):
        self.discord.send_status(f"PredictionEngine has started a new run. (Git hash: `{Logger.git_hash()}`)")
        self.delphi.run()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.delphi.stop()
            self.log.debug('KeyboardInterrupt')
            
if __name__ == '__main__':
    PredictionEngine().run()