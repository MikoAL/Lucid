import asyncio
import websockets
import logging
import json
import os
from dotenv import load_dotenv

async def send_message(uri, message):
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
        print(f"Sent: {message}")

async def receive_message(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

"""async def main():
    uri = "ws://localhost:8000/ws/1"  # Change client_id as needed
    await asyncio.gather(
        send_message(uri, "Hello, WebSocket!"),
        receive_message(uri),
    )"""

# ===== ===== ===== #
# Server Handler
load_dotenv()
GUILD = os.getenv('DISCORD_GUILD_ID')

class ServerHandler():
    def __init__(self, server):
        self.uri = f"{server}/ws/main_script"
        self.read_mails = []
        self.unread_mails = []
        self.websocket = None  # Initialize WebSocket connection
        
    async def connect(self):
        self.websocket = await websockets.connect(self.uri)

    async def check_mailbox(self) -> None:
        logging.info(f"Checking mailbox")
        await self.websocket.send("CHECK_MAILBOX")
        response = await self.websocket.recv()
        new_mails = json.loads(response)
        logging.info(f"Got: {new_mails}")
        if new_mails:
            logging.info(f"Got new mails: {new_mails}")
            self.unread_mails.extend(new_mails)
    
    def get_unread_mails(self) -> list:
        asyncio.run(self.check_mailbox())
        temp_unread_mails = self.unread_mails.copy()
        self.read_mails.extend(self.unread_mails)
        self.unread_mails = []
        return temp_unread_mails
    
    async def send_discord_message(self, message):
        await self.websocket.send(json.dumps({"type": "discord_message", "content": message}))

    async def logging_to_discord(self, message):
        await self.websocket.send(json.dumps({"type": "log", "content": message}))

# Example usage:
async def main():
    server_handler = ServerHandler("ws://localhost:8000")
    await server_handler.connect()  # Connect to WebSocket server
    await server_handler.send_discord_message("Hello, Discord!")
    print(f"sent message")
    await server_handler.logging_to_discord("Logging message")
    print(f"logged message")

asyncio.run(main())
#server_handler = ServerHandler("ws://localhost:8000")
#server_handler.send_discord_message("Hello, Discord!")
#asyncio.run(main())
