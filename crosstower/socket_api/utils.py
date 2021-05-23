import json
import os

def handle_response(response: str):
    response = json.loads(response)
    if response.get('error'):
        err = f"API responded with error {response['error']['code']}: '{response['error']['message']}'"
        raise Exception(err)
    return response

def get_last_line(filepath: str) -> str:
    '''
    Efficient method for retrieving the last line of a text file, without parsing the entire file.
    
    Does not check for file existence, and will crash if not exist
    '''
    with open(filepath, 'rb') as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        return f.readline().decode()

scraper_startup_message = '''
        All threads are running. Runtime options:

        `status`  : General scraping data
        `exit`    : Quit entire program
        `restart` : Reboot websocket
        '''

scraper_exit_message = '''
        Waiting for all threads to close...
        Hard reset of terminal may be necessary if frozen
        '''

scraper_restart_message = '''
        Unplugged socket, plugging back in...
        '''