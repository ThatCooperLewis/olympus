import json
import os
from time import strftime, localtime


def handle_response(response: str):
    response = json.loads(response)
    if response.get('error'):
        err = f"API responded with error {response['error']['code']}: '{response['error']['message']}'"
        raise Exception(err)
    return response

scraper_startup_message = '''
        All threads are running. Runtime options:

        `status`  : General scraping data
        `restart` : Reboot websocket
        `help`    : Show these options
        `exit`    : Quit entire program
        '''

scraper_exit_message = '''
        Waiting for all threads to close...
        Hard reset of terminal may be necessary if frozen
        '''

scraper_restart_message = '''
        Unplugged socket, plugging back in...
        '''

def print_status_message(last_time, attempt_count):
    last_updated = strftime('%Y-%m-%d %H:%M:%S', localtime(last_time))
    print(f'''================================================
    Last recorded time: {last_updated}
    Connection attempt: {attempt_count + 1}
================================================''')