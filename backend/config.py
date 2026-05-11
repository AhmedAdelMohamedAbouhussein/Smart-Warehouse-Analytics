"""
Smart Warehouse System — Configuration
Central configuration for warehouse dimensions, simulation parameters, and defaults.
"""

# ─── Warehouse Layout ────────────────────────────────────────────────
WAREHOUSE_ROWS = 30
WAREHOUSE_COLS = 80

# Zone boundaries (row ranges, 0-indexed from top)
ZONE_RECEIVING = (0, 1)        # Top row: receiving dock
ZONE_C = (2, 8)                # Far from stations: low velocity
ZONE_B = (9, 15)               # Mid-range: medium velocity
ZONE_A = (16, 26)              # Close to stations: high velocity
ZONE_PICK_STATIONS = (27, 29)  # Bottom rows: pick/pack stations

# Aisle layout pattern within zones
AISLE_WIDTH = 1                # Path columns between shelf pairs
SHELF_PAIR_WIDTH = 2           # Two shelves side by side

# Shelf capacity (arbitrary cubic units)
SHELF_CAPACITY = 100.0

# ─── Simulation ──────────────────────────────────────────────────────
SIMULATION_TICK_MS = 200          # Milliseconds per simulation tick
DEFAULT_SPEED_MULTIPLIER = 1.0   # 1x speed
MAX_SPEED_MULTIPLIER = 10.0
MIN_SPEED_MULTIPLIER = 0.25

# Picker movement speed (cells per tick at 1x speed)
PICKER_SPEED = 1

# Number of pickers
DEFAULT_PICKER_COUNT = 8

# ─── Order Generation ────────────────────────────────────────────────
ORDER_ARRIVAL_RATE = 0.05       # 1 order every ~4 seconds at 1x speed
MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 5

# ─── Replenishment ───────────────────────────────────────────────────
DEFAULT_REORDER_THRESHOLD = 5
REPLENISHMENT_QUANTITY = 20

# ─── Products ─────────────────────────────────────────────────────────
NUM_PRODUCTS = 100

# ABC Classification thresholds (cumulative % of demand)
ABC_A_THRESHOLD = 0.20   # Top 20% of demand → Class A
ABC_B_THRESHOLD = 0.50   # Next 30% → Class B
                          # Bottom 50% → Class C

# ─── Graph Weights ────────────────────────────────────────────────────
EDGE_WEIGHT_STRAIGHT = 1.0
EDGE_WEIGHT_TURN = 1.2       # Slight penalty for turns
EDGE_WEIGHT_CONGESTED = 2.0  # Congestion multiplier

# ─── Server ───────────────────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 8000
CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
