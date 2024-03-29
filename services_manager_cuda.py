from services.prediction_engine import PredictionEngine
from services.continuous_integration import IntegrationService
from utils import DiscordWebhook
from utils.environment import env
import sys

def get_service(service_name: str):
    if service_name == 'prediction':
        return PredictionEngine()
    elif service_name == 'integration':
        return IntegrationService()
    return None

def handle(service_name: str):
    discord = DiscordWebhook('ServicesManager')
    try:
        service = get_service(env.service_name)
        if service:
            service.run()
        else:
            print('Invalid service name.')
            print('Usage: python3 services_manager.py <prediction>')
            exit(1)
    except KeyboardInterrupt:
        discord.send_status('KeyboardInterrupt halted service')
    except SystemExit:
        discord.send_status('sys.exit() halted service, likely and invalid service_name argument')
    except Exception as e:
        discord.send_alert(f'Unknown error halted service during services_manager_cuda: {e}')
    
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        handle(sys.argv[1])
    else:
        handle(None)