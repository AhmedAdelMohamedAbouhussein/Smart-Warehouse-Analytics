"""
Smart Warehouse System — Order Model
Represents customer orders with items to pick from the warehouse.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class OrderStatus(str, Enum):
    """Order lifecycle states."""
    PENDING = "pending"         # Waiting for picker assignment
    ASSIGNED = "assigned"       # Assigned to a picker
    PICKING = "picking"         # Picker is actively picking items
    COMPLETED = "completed"     # All items picked, order done
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    """A single item within an order."""
    product_id: int
    product_name: str = ""
    quantity: int = Field(ge=1, default=1)
    shelf_location: Optional[tuple[int, int]] = None  # Where to pick from

    model_config = {"arbitrary_types_allowed": True}


class Order(BaseModel):
    """A customer order consisting of multiple items to pick."""
    id: int
    status: OrderStatus = OrderStatus.PENDING
    items: list[OrderItem] = []
    assigned_picker_id: Optional[int] = None
    # Timestamps
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    assigned_at: Optional[float] = None
    completed_at: Optional[float] = None
    # Metrics
    total_distance: float = 0.0          # Total travel distance for this order
    pick_route: list[tuple[int, int]] = []  # Ordered list of locations to visit
    optimized_route: list[tuple[int, int]] = []  # Route after optimization

    @property
    def cycle_time(self) -> Optional[float]:
        """Time from creation to completion in seconds."""
        if self.completed_at and self.created_at:
            return self.completed_at - self.created_at
        return None

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)

    model_config = {"arbitrary_types_allowed": True}


class OrderCreate(BaseModel):
    """Schema for manually creating an order."""
    items: list[dict] = Field(
        description="List of {product_id, quantity} dicts"
    )
