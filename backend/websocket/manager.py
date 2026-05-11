"""
Smart Warehouse System — WebSocket Connection Manager
Manages WebSocket connections and broadcasts simulation state to all clients.
"""
import json
from fastapi import WebSocket
from typing import Any
from utils import sanitize_json


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts messages."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, data: Any):
        """Send data to all connected clients."""
        if not self.active_connections:
            return

        message = json.dumps(sanitize_json(data), default=str)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal(self, websocket: WebSocket, data: Any):
        """Send data to a specific client."""
        try:
            message = json.dumps(sanitize_json(data), default=str)
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)

    @property
    def client_count(self) -> int:
        return len(self.active_connections)
