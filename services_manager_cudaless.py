from services import PostgresMonitor, TickerScraper, OrderListener
from utils import DiscordWebhook
from utils.environment import env
import sys
from os import getenv


def get_service(service_name: str):
    if service_name == 'scraper':
        return TickerScraper()
    elif service_name == 'monitor':
        return PostgresMonitor()
    elif service_name == 'orders':
        return OrderListener()
    return None

def handle(service_name: str = None):
    discord = DiscordWebhook('ServicesManager')
    try:
        service = get_service(env.service_name)
        if service:
            service.run()
        else:
            print(f'Invalid service name: "{env.service_name}"')
            print('Usage: python3 services_manager.py <scraper|monitor|orders>')
            exit(1)
    except KeyboardInterrupt:
        discord.send_status('KeyboardInterrupt halted service')
    except SystemExit:
        discord.send_status('sys.exit() halted service, likely and invalid service_name argument')
    except Exception as e:
        discord.send_alert(f'Unknown error halted service during services_manager: {e}')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle(sys.argv[1])
    else:
        handle(None)