import json
import os
from time import strftime, localtime

def handle_response(response: str):
    response = json.loads(response)
    if response.get('error'):
        err = f"API responded with error {response['error']['code']}: '{response['error']['message']}'"
        raise Exception(err)
    return response

def get_newest_line(filepath: str) -> str:
    '''
    Efficient method for retrieving the newest/last line of a text file, without parsing the entire file.
    
    Does not check for file existence, and will crash if not exist.
    '''
    with open(filepath, 'rb') as f:
        for i in range(-2, 0):
            # f.seek(-2) will crash if file is only one line
            try:
                f.seek(i, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(i, os.SEEK_CUR)
                return f.readline().decode()
            except OSError:
                continue
        return ""

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