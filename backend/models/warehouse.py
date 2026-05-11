from __future__ import annotations
"""
Smart Warehouse System — Warehouse Layout Model
Defines the warehouse grid, cell types, and layout generation.
"""

from pydantic import BaseModel
from enum import Enum
from typing import Optional
import config


class CellType(str, Enum):
    """Types of cells in the warehouse grid."""
    PATH = "path"               # Walkable aisle
    SHELF = "shelf"             # Storage shelf/rack
    PICK_STATION = "pick_station"  # Packing/shipping station
    RECEIVING = "receiving"     # Inbound receiving dock
    EMPTY = "empty"             # Unused space
    WALL = "wall"               # Wall/boundary


class WarehouseCell(BaseModel):
    """A single cell in the warehouse grid."""
    row: int
    col: int
    cell_type: CellType = CellType.EMPTY
    zone: Optional[str] = None           # "A", "B", "C", "station", "receiving"
    shelf_id: Optional[int] = None       # Unique shelf identifier
    shelf_capacity: float = 0.0          # Max volume this shelf can hold
    shelf_used: float = 0.0              # Currently used volume
    products: list[int] = []             # Product IDs stored here
    visit_count: int = 0                 # For heatmap tracking

    @property
    def is_walkable(self) -> bool:
        return self.cell_type in (CellType.PATH, CellType.PICK_STATION, CellType.RECEIVING)

    @property
    def utilization(self) -> float:
        if self.shelf_capacity == 0:
            return 0.0
        return (self.shelf_used / self.shelf_capacity) * 100


class WarehouseLayout(BaseModel):
    """Full warehouse grid layout."""
    rows: int = config.WAREHOUSE_ROWS
    cols: int = config.WAREHOUSE_COLS
    grid: list[list[dict]] = []
    shelf_count: int = 0
    path_count: int = 0

    @staticmethod
    def generate_default() -> "WarehouseLayout":
        """
        Generate a realistic warehouse layout with:
        - Receiving dock at top
        - ABC-zoned shelf rows with aisles
        - Pick stations at bottom
        """
        rows = config.WAREHOUSE_ROWS
        cols = config.WAREHOUSE_COLS
        grid = []
        shelf_id_counter = 0

        for r in range(rows):
            row_cells = []
            for c in range(cols):
                cell = {
                    "row": r,
                    "col": c,
                    "cell_type": CellType.EMPTY.value,
                    "zone": None,
                    "shelf_id": None,
                    "shelf_capacity": 0.0,
                    "shelf_used": 0.0,
                    "products": [],
                    "visit_count": 0,
                }

                # ── Receiving dock (top row) ──
                if r == 0:
                    cell["cell_type"] = CellType.RECEIVING.value
                    cell["zone"] = "receiving"

                # ── Pick stations (bottom 2 rows) ──
                elif r >= rows - 2:
                    if c % 6 == 2 or c % 6 == 3:
                        cell["cell_type"] = CellType.PICK_STATION.value
                        cell["zone"] = "station"
                    else:
                        cell["cell_type"] = CellType.PATH.value
                        cell["zone"] = "station"

                # ── Main warehouse area ──
                elif 1 <= r <= rows - 3:
                    # Determine zone based on row
                    if config.ZONE_C[0] <= r <= config.ZONE_C[1]:
                        zone = "C"
                    elif config.ZONE_B[0] <= r <= config.ZONE_B[1]:
                        zone = "B"
                    else:
                        zone = "A"

                    # Left and right border paths
                    if c == 0 or c == cols - 1:
                        cell["cell_type"] = CellType.PATH.value
                        cell["zone"] = zone
                    # Cross-aisle paths (every 8th row in warehouse area)
                    elif (r - 1) % 8 == 0:
                        cell["cell_type"] = CellType.PATH.value
                        cell["zone"] = zone
                    # Vertical aisle pattern: PATH SHELF SHELF PATH SHELF SHELF ...
                    else:
                        col_pattern = (c - 1) % 4  # 0=path, 1=shelf, 2=shelf, 3=path
                        if col_pattern == 0 or col_pattern == 3:
                            cell["cell_type"] = CellType.PATH.value
                            cell["zone"] = zone
                        else:
                            cell["cell_type"] = CellType.SHELF.value
                            cell["zone"] = zone
                            cell["shelf_id"] = shelf_id_counter
                            cell["shelf_capacity"] = config.SHELF_CAPACITY
                            shelf_id_counter += 1

                row_cells.append(cell)
            grid.append(row_cells)

        layout = WarehouseLayout(
            rows=rows,
            cols=cols,
            grid=grid,
            shelf_count=shelf_id_counter,
        )
        # Count paths
        layout.path_count = sum(
            1 for row in grid for cell in row
            if cell["cell_type"] in (CellType.PATH.value, CellType.PICK_STATION.value, CellType.RECEIVING.value)
        )
        return layout
