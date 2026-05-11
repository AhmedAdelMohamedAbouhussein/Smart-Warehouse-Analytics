from __future__ import annotations
"""
Smart Warehouse System — FastAPI Application Entry Point
Main server with REST API, WebSocket, and simulation engine integration.
"""
import sys
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import config
from simulation.engine import SimulationEngine
from websocket.manager import ConnectionManager
from routers import warehouse, orders, simulation, algorithms, analytics
from database import init_db

# ── Lifespan ──────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the simulation engine on server start."""
    init_db()
    simulation_engine.initialize()
    simulation_engine.set_broadcast_callback(ws_manager.broadcast)
    print("[OK] Smart Warehouse System initialized")
    print(f"   Warehouse: {config.WAREHOUSE_ROWS}x{config.WAREHOUSE_COLS} grid")
    print(f"   Products: {len(simulation_engine.products)}")
    print(f"   Pickers: {len(simulation_engine.pickers)}")
    print(f"   Graph nodes: {len(simulation_engine.graph.nodes)}")
    yield  # server is running


# ── Application Setup ─────────────────────────────────────────────────
app = FastAPI(
    title="Smart Warehouse System",
    description="Interactive warehouse simulation demonstrating Dijkstra, Bin Packing, Held-Karp DP, and Greedy algorithms",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Instances ──────────────────────────────────────────────────
simulation_engine = SimulationEngine()
ws_manager = ConnectionManager()

# ── Register Routers ──────────────────────────────────────────────────
app.include_router(warehouse.router)
app.include_router(orders.router)
app.include_router(simulation.router)
app.include_router(algorithms.router)
app.include_router(analytics.router)





# ── WebSocket Endpoint ────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time simulation updates."""
    await ws_manager.connect(websocket)
    try:
        # Send initial state
        await ws_manager.send_personal(websocket, {
            "type": "system_init",
            "message": "Connected to Smart Warehouse simulation",
            "state": simulation_engine.get_state()
        })
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await ws_manager.send_personal(websocket, {"type": "pong"})
            except json.JSONDecodeError:
                if data == "ping":
                    await ws_manager.send_personal(websocket, {"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# ── Health Check ──────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": "Smart Warehouse System",
        "status": "running",
        "simulation": {
            "running": simulation_engine.running,
            "tick": simulation_engine.tick_count,
            "connected_clients": ws_manager.client_count,
        },
    }


# ── Run Server ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)
