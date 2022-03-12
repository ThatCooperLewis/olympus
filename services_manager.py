from matplotlib.axis import Tick
from services import TickerMonitor, TickerScraper
import sys

def get_service(service_name: str):
    if service_name == 'scraper':
        return TickerScraper()
    elif service_name == 'monitor':
        return TickerMonitor()
    return None

if __name__ == "__main__":
    service = get_service(sys.argv[1])
    if service:
        service.run()
    else:
        print('Invalid service name.')
        print('Usage: python3 services_manager.py <scraper|monitor>')
        exit(1)