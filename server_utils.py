from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from websockets.exceptions import ConnectionClosed
from typing import List
import logging
import json

class ClientConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.server_websocket = websocket

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
