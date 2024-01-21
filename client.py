import requests
import yaml
import os

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))

# Change the working directory to the script's directory
os.chdir(script_dir)
# Example data
"""
data = {
    'name': 'John Doe',
    'age': 30,
    'city': 'Example City',
    'skills': ['Python', 'JavaScript', 'SQL']
}

# Writing to a YAML file
with open('settings.yaml', 'w') as file:
    yaml.dump(data, file)
"""
# Reading from a YAML file
with open('settings.yaml', 'r') as file:
    settings = yaml.safe_load(file)

host = settings['host']
port = settings['port']
server = f'http://{host}:{port}'
print(server)
print((requests.get(server)).json()['message'])