"""
Smart Warehouse System — Simulation Control API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
import asyncio

from utils import sanitize_json

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


class SpeedRequest(BaseModel):
    speed: float = 1.0


@router.get("/state")
async def get_state():
    """Get current simulation state snapshot."""
    from main import simulation_engine
    return sanitize_json(simulation_engine.get_state())


@router.post("/start")
async def start_simulation():
    """Start the simulation."""
    from main import simulation_engine
    if not simulation_engine.running:
        asyncio.create_task(simulation_engine.start())
    elif simulation_engine.paused:
        await simulation_engine.resume()
    return {"status": "running", "tick": simulation_engine.tick_count}


@router.post("/pause")
async def pause_simulation():
    """Pause the simulation."""
    from main import simulation_engine
    await simulation_engine.pause()
    return {"status": "paused", "tick": simulation_engine.tick_count}


@router.post("/reset")
async def reset_simulation():
    """Reset the simulation to initial state."""
    from main import simulation_engine
    simulation_engine.reset()
    return {"status": "reset", "tick": 0}


@router.put("/speed")
async def set_speed(req: SpeedRequest):
    """Set simulation speed multiplier."""
    from main import simulation_engine
    simulation_engine.set_speed(req.speed)
    return {"speed": simulation_engine.speed}
