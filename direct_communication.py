from voice_recognition.voice_recognition import VoiceRecognition
import os
import yaml
import logging
import time
import json
import asyncio

import websockets

from dotenv import load_dotenv

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))
# Change the working directory to the script's directory
os.chdir(script_dir)

# Reading from a YAML file
with open('settings.yaml', 'r') as file:
    settings = yaml.safe_load(file)

host = settings['host']
port = settings['port']
server_ws_uri = f"ws://{host}:{port}/ws/voice_recognition"

class ConnectionManager:
    def __init__(self):
        self.server_websocket = None

    async def connect_to_server(self):
        self.server_websocket = await websockets.connect(server_ws_uri)

    async def send_to_server(self, message): 
        print("Sending message to server:", message)
        await self.server_websocket.send(json.dumps(message))

connection_manager = ConnectionManager()

def send_message(message: str):
    global connection_manager
    asyncio.run(connection_manager.send_to_server({"content": message,"source": "Miko" ,"timestamp": time.time(), "type": "voice_message"}))

demo = VoiceRecognition(wake_word=None, function=send_message)
demo.start()

