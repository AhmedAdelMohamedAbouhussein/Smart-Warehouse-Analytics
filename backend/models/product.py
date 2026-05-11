"""
Smart Warehouse System — Product Model
Represents items stored in the warehouse with ABC velocity classification.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class VelocityClass(str, Enum):
    """ABC classification based on demand frequency."""
    A = "A"  # High velocity — top 20% demand
    B = "B"  # Medium velocity — next 30%
    C = "C"  # Low velocity — bottom 50%


class Product(BaseModel):
    """A product stored in the warehouse."""
    id: int
    name: str
    sku: str
    # Physical dimensions (arbitrary units)
    width: float = Field(ge=0.1, le=10.0)
    height: float = Field(ge=0.1, le=10.0)
    depth: float = Field(ge=0.1, le=10.0)
    weight: float = Field(ge=0.1, le=50.0)
    # Classification
    velocity_class: VelocityClass = VelocityClass.C
    demand_frequency: float = Field(ge=0.0, description="Average orders per hour")
    # Inventory
    current_stock: int = Field(ge=0, default=20)
    reorder_threshold: int = Field(ge=0, default=5)
    # Location
    shelf_location: Optional[tuple[int, int]] = None  # (row, col) on warehouse grid

    @property
    def volume(self) -> float:
        """Calculate product volume."""
        return self.width * self.height * self.depth

    model_config = {"arbitrary_types_allowed": True}


class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    name: str
    sku: str
    width: float = 1.0
    height: float = 1.0
    depth: float = 1.0
    weight: float = 1.0
    demand_frequency: float = 1.0
    current_stock: int = 20
    reorder_threshold: int = 5
