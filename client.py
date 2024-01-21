import requests
import yaml
import os
import logging
import time
import json
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))
# Change the working directory to the script's directory
os.chdir(script_dir)

# Reading from a YAML file
with open('settings.yaml', 'r') as file:
    settings = yaml.safe_load(file)

host = settings['host']
port = settings['port']
server = f'http://{host}:{port}'

user_name = settings['user_name']

try:
    response = requests.get(server)
    response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
    logging.info(f"Server response: {response.status_code}")
except requests.exceptions.RequestException as e:
    logging.critical(f'Failed to connect to the server')
    exit()
headers = {'Content-Type': 'application/json'}

def send_message(message, user_name=user_name, server=server):
    requests.post(url=f'{server}/postbox', json=({'content':message,'source':user_name,'timestamp':time.time()}))
    return

send_message('Testtttt')
new_mail = (requests.get(url = f"{server}/mailbox")).json()
print(new_mail)
new_mail = (requests.get(url = f"{server}/mailbox")).json()
print(new_mail)