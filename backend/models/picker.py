"""
Smart Warehouse System — Picker Model
Represents warehouse workers who pick items from shelves.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PickerStatus(str, Enum):
    """Picker activity states."""
    IDLE = "idle"                 # Waiting at station for next order
    TRAVELING = "traveling"       # Moving to next pick location
    PICKING = "picking"           # At a shelf, picking an item
    RETURNING = "returning"       # Returning to pick station
    REPLENISHING = "replenishing" # Performing a replenishment task


class Picker(BaseModel):
    """A warehouse picker/worker."""
    id: int
    name: str
    status: PickerStatus = PickerStatus.IDLE
    # Position
    current_position: tuple[int, int] = (0, 0)  # (row, col)
    home_station: tuple[int, int] = (0, 0)       # Assigned pick station
    # Current task
    assigned_order_id: Optional[int] = None
    route: list[tuple[int, int]] = []             # Full path to follow
    route_index: int = 0                          # Current position in route
    current_target: Optional[tuple[int, int]] = None  # Next stop
    # Metrics
    total_distance_traveled: float = 0.0
    orders_completed: int = 0
    total_idle_time: float = 0.0
    total_active_time: float = 0.0
    # Visual
    color: str = "#00ff88"  # Display color on map

    @property
    def utilization(self) -> float:
        """Percentage of time spent actively working."""
        total = self.total_idle_time + self.total_active_time
        if total == 0:
            return 0.0
        return (self.total_active_time / total) * 100

    @property
    def is_available(self) -> bool:
        """Whether this picker can accept a new order."""
        return self.status == PickerStatus.IDLE

    model_config = {"arbitrary_types_allowed": True}
