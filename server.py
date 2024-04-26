from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from websockets.exceptions import ConnectionClosed
from typing import List
import logging
import json
import time
import asyncio
app = FastAPI()
# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info('API is starting up')
logger.debug('Debugging is enabled')
uncollected_mails = []

class ServerConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def connect_mainscript(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.mainscript_websocket = websocket
        await self.log_to_discord("main_script connected")
    
    async def connect_discord_handler(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.discord_handler_websocket = websocket
        await self.log_to_discord("discord_handler connected")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            logging.info(f"Sending message to {connection}")
            await connection.send_text(message)
    
    async def send_to_mainscript(self, information: dict):
        await self.mainscript_websocket.send_text(json.dumps(information))        
    
    async def log_to_discord(self, message: str):
        logger.info(f"Logging message: {message}")
        await self.discord_handler_websocket.send_text(json.dumps({"type": "log", "content": message}))
    async def send_discord_message(self, message: str):
        await self.discord_handler_websocket.send_text(json.dumps({"type": "Lucid_discord_message", "content": message}))
    
manager = ServerConnectionManager()


@app.websocket("/ws/discord_handler")
async def discord_handler_endpoint(websocket: WebSocket):
    global uncollected_mails
    await manager.connect_discord_handler(websocket)
    try:
        while True:
            message = await manager.discord_handler_websocket.receive_text()
            logger.info(f"Received message from discord handler: {message}")
            data = json.loads(message)
            message_type = data.get("type")
            content = data.get("content")
            match message_type:
                case "discord_user_message":
                    message = {'content':content,'source':data.get('source'),'timestamp':data.get('timestamp'), 'type':'discord_user_message'}
                    uncollected_mails.append(message)
                    logger.info(f"Added message to mailbox: {message}")

    except (WebSocketDisconnect, ConnectionClosed):
        manager.disconnect(websocket)
        logger.info(f"discord_handler has disconnected")

@app.websocket("/ws/main_script")
async def main_script_endpoint(websocket: WebSocket):
    await manager.connect_mainscript(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            logger.info(f"Received message: {message}")
            data = json.loads(message)
            message_type = data.get("type")
            content = data.get("content")
            match message_type:
                
                case "command":
                    match data.get("command_type"):
                        
                        case "collect_mailbox":
                            global uncollected_mails
                            logger.info(f"Asked to for mailbox to be collected")
                            logger.info(f"{json.dumps(uncollected_mails)}")
                            await websocket.send_text(json.dumps(uncollected_mails))
                            logger.info(f"Mailbox collected")
                            uncollected_mails = []

                        case "log":
                            # Handle log message
                            logger.info(f"Logging message: {content}")
                            await manager.log_to_discord(content)
                            # Log the content...
                
                case "Lucid_output":
                    match data.get("output_type"):
                        case "discord_message":
                            # Handle summary output
                            await manager.send_discord_message(content)
                            # Log the content...


    except (WebSocketDisconnect, ConnectionClosed) as e:
        logger.info(f"main_script has disconnected because of {e}")
        manager.disconnect(websocket)
        await manager.log_to_discord(f"main_script has disconnected because of {e}")