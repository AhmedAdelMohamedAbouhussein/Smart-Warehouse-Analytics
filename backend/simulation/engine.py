"""
Smart Warehouse System — Core Simulation Engine
Tick-based simulation loop managing orders, pickers, and warehouse state.
"""
from __future__ import annotations
import time
import random
import asyncio
from typing import Optional
import config
from models.warehouse import WarehouseLayout, CellType
from simulation.warehouse_graph import WarehouseGraph
from simulation.order_generator import OrderGenerator
from simulation.replenishment import ReplenishmentManager
from algorithms.dijkstra import dijkstra, multi_stop_dijkstra, compute_distance_matrix
from algorithms.bin_packing import optimize_slotting
from algorithms.held_karp import held_karp_tsp
from algorithms.greedy_assignment import assign_order_greedy


class SimulationEngine:
    """
    Core simulation engine that drives the warehouse simulation.
    Runs a tick-based loop: generate orders → assign pickers → move pickers → check completions → replenish.
    """

    def __init__(self):
        self.running = False
        self.paused = False
        self.speed = config.DEFAULT_SPEED_MULTIPLIER
        self.tick_count = 0

        # Warehouse
        self.layout: Optional[WarehouseLayout] = None
        self.graph = WarehouseGraph()

        # Entities
        self.products: dict[int, dict] = {}
        self.orders: dict[int, dict] = {}
        self.pickers: dict[int, dict] = {}

        # Subsystems
        self.order_generator: Optional[OrderGenerator] = None
        self.replenishment = ReplenishmentManager()

        # Metrics
        self.events: list[dict] = []
        self.completed_orders: list[dict] = []
        self.total_distance = 0.0
        self.heatmap: dict[tuple[int, int], int] = {}

        # Callback for broadcasting state
        self._broadcast_callback = None

    def set_broadcast_callback(self, callback):
        """Set the async callback for broadcasting state updates."""
        self._broadcast_callback = callback

    def initialize(self):
        """Initialize warehouse layout, products, pickers, and graph."""
        # Generate warehouse layout
        self.layout = WarehouseLayout.generate_default()
        self.graph.build_from_layout(self.layout)

        # Generate products
        self._generate_products()

        # Run initial slotting optimization
        self._run_slotting()

        # Initialize pickers at pick stations
        self._initialize_pickers()

        # Initialize order generator
        product_list = list(self.products.values())
        self.order_generator = OrderGenerator(product_list)

        self._add_event("system", "Warehouse initialized successfully")

    def _generate_products(self):
        """Generate a catalog of products with varying demand frequencies."""
        product_names = [
            "Wireless Mouse", "USB-C Cable", "Laptop Stand", "Webcam HD", "Mechanical Keyboard",
            "Monitor Arm", "Desk Lamp", "Headset Pro", "Mouse Pad XL", "USB Hub",
            "Phone Charger", "HDMI Cable", "Ethernet Cable", "Power Strip", "Cable Clips",
            "Screen Cleaner", "Keyboard Cover", "Wrist Rest", "Document Holder", "Pen Cup",
            "Notebook A5", "Sticky Notes", "Binder Clips", "Tape Dispenser", "Scissors",
            "Stapler", "Paper Clips", "Highlighters", "Dry Erase Markers", "Whiteboard Eraser",
            "Desk Organizer", "File Folders", "Label Maker", "Calculator", "Desk Clock",
            "Water Bottle", "Coffee Mug", "Coasters Set", "Plant Pot", "Air Purifier",
            "Desk Fan", "Space Heater", "Surge Protector", "Battery Pack", "Flash Drive",
            "SD Card", "Webcam Cover", "Blue Light Glasses", "Footrest", "Back Cushion",
        ]

        for i in range(min(config.NUM_PRODUCTS, len(product_names))):
            # Higher index = lower demand (Pareto-like distribution)
            demand = round(max(0.1, 10.0 / (1 + i * 0.5) + random.uniform(-0.5, 0.5)), 2)
            self.products[i] = {
                "id": i,
                "name": product_names[i],
                "sku": f"SKU-{1000 + i}",
                "width": round(random.uniform(0.5, 3.0), 1),
                "height": round(random.uniform(0.5, 3.0), 1),
                "depth": round(random.uniform(0.5, 2.0), 1),
                "weight": round(random.uniform(0.2, 10.0), 1),
                "velocity_class": "C",  # Will be set by slotting
                "demand_frequency": demand,
                "current_stock": random.randint(10, 30),
                "reorder_threshold": config.DEFAULT_REORDER_THRESHOLD,
                "shelf_location": None,
            }

    def _run_slotting(self):
        """Run bin packing slotting optimization to assign products to shelves."""
        product_list = list(self.products.values())

        # Collect shelf info from layout
        shelves = []
        for r in range(self.layout.rows):
            for c in range(self.layout.cols):
                cell = self.layout.grid[r][c]
                if cell["cell_type"] == CellType.SHELF.value and cell.get("shelf_id") is not None:
                    shelves.append({
                        "id": cell["shelf_id"],
                        "capacity": cell["shelf_capacity"],
                        "row": r, "col": c,
                        "zone": cell.get("zone", "C"),
                    })

        result = optimize_slotting(product_list, shelves)

        # Apply placements
        for pid_str, shelf_id in result["placements"].items():
            pid = int(pid_str) if isinstance(pid_str, str) else pid_str
            if pid in self.products:
                # Find shelf position
                for shelf in shelves:
                    if shelf["id"] == shelf_id:
                        self.products[pid]["shelf_location"] = [shelf["row"], shelf["col"]]
                        break

        # Update velocity classes from classification
        for detail in result.get("classification", {}).get("details", []):
            pid = detail["id"]
            if pid in self.products:
                self.products[pid]["velocity_class"] = detail["velocity_class"]

        # Update layout grid with product assignments
        for pid, product in self.products.items():
            loc = product.get("shelf_location")
            if loc:
                r, c = loc
                cell = self.layout.grid[r][c]
                if pid not in cell["products"]:
                    cell["products"].append(pid)
                vol = product["width"] * product["height"] * product["depth"]
                cell["shelf_used"] += vol

    def _initialize_pickers(self):
        """Create pickers at pick stations."""
        stations = self.graph.get_pick_stations(self.layout)
        colors = ["#00ff88", "#00ccff", "#ff6b6b", "#ffd93d", "#c084fc", "#fb923c"]

        for i in range(config.DEFAULT_PICKER_COUNT):
            station = stations[i % len(stations)] if stations else (self.layout.rows - 1, 1)
            self.pickers[i] = {
                "id": i,
                "name": f"Picker {i + 1}",
                "status": "idle",
                "current_position": list(station),
                "home_station": list(station),
                "assigned_order_id": None,
                "route": [],
                "route_index": 0,
                "current_target": None,
                "total_distance_traveled": 0.0,
                "orders_completed": 0,
                "total_idle_time": 0.0,
                "total_active_time": 0.0,
                "color": colors[i % len(colors)],
            }

    async def start(self):
        """Start the simulation loop."""
        if not self.layout:
            self.initialize()
        self.running = True
        self.paused = False
        self._add_event("system", "Simulation started")
        await self._run_loop()

    async def pause(self):
        """Pause the simulation."""
        self.paused = True
        self._add_event("system", "Simulation paused")

    async def resume(self):
        """Resume the simulation."""
        self.paused = False
        self._add_event("system", "Simulation resumed")

    def reset(self):
        """Reset the simulation to initial state."""
        self.running = False
        self.paused = False
        self.tick_count = 0
        self.orders.clear()
        self.completed_orders.clear()
        self.events.clear()
        self.total_distance = 0.0
        self.heatmap.clear()
        self.replenishment = ReplenishmentManager()
        self.initialize()
        self._add_event("system", "Simulation reset")
        
        # Immediate broadcast to sync UI
        if self._broadcast_callback:
            # We can't await here as reset is sync, but we can use create_task
            asyncio.create_task(self._broadcast_callback(self.get_state()))

    def set_speed(self, multiplier: float):
        """Set simulation speed multiplier."""
        self.speed = max(config.MIN_SPEED_MULTIPLIER, min(multiplier, config.MAX_SPEED_MULTIPLIER))

    async def _run_loop(self):
        """Main simulation tick loop."""
        while self.running:
            if not self.paused:
                await self._tick()
            tick_interval = config.SIMULATION_TICK_MS / 1000.0 / self.speed
            await asyncio.sleep(tick_interval)

    async def _tick(self):
        """Execute one simulation tick."""
        self.tick_count += 1

        # 1. Generate new orders
        self._generate_orders()

        # 2. Assign pending orders to idle pickers
        self._assign_orders()

        # 3. Move pickers along their routes
        self._move_pickers()

        # 4. Check for order completions
        self._check_completions()

        # 5. Check replenishment needs (every 10 ticks)
        if self.tick_count % 10 == 0:
            self._check_replenishment()

        # 6. Advance replenishment tasks
        self.replenishment.advance_tasks()

        # 7. Update picker time tracking
        self._update_time_tracking()

        # 8. Broadcast state to all connected clients
        if self._broadcast_callback:
            await self._broadcast_callback(self.get_state())

    def _generate_orders(self):
        """Generate new customer orders based on Poisson arrival."""
        if self.order_generator and self.order_generator.should_generate():
            order = self.order_generator.generate_order(self.products)
            if order:
                self.orders[order["id"]] = order
                self._add_event("order", f"New order #{order['id']} ({len(order['items'])} items)")

    def _assign_orders(self):
        """Assign pending orders to available pickers using greedy algorithm."""
        pending = [o for o in self.orders.values() if o["status"] == "pending"]
        if not pending:
            return

        for order in pending:
            # Build distance function using graph
            def dist_func(a, b):
                return self.graph.distance(tuple(a), tuple(b))

            picker_list = list(self.pickers.values())
            result = assign_order_greedy(order, picker_list, dist_func)

            if result["assigned_picker_id"] is not None:
                picker_id = result["assigned_picker_id"]
                self._assign_order_to_picker(order, picker_id)

    def _assign_order_to_picker(self, order: dict, picker_id: int):
        """Assign an order to a specific picker and compute pick route."""
        picker = self.pickers[picker_id]
        order["status"] = "assigned"
        order["assigned_picker_id"] = picker_id
        order["assigned_at"] = time.time()

        # Collect pick locations
        pick_locations = []
        for item in order["items"]:
            loc = item.get("shelf_location")
            if loc:
                access = self.graph.get_location_for_cell(loc[0], loc[1])
                if access and access not in pick_locations:
                    pick_locations.append(access)

        if not pick_locations:
            order["status"] = "completed"
            order["completed_at"] = time.time()
            return

        order["pick_route"] = [list(loc) for loc in pick_locations]

        # Optimize route with Held-Karp if small enough, else use greedy
        start_pos = tuple(picker["current_position"])
        all_locs = [start_pos] + pick_locations

        if len(all_locs) <= 15:
            dist_matrix = compute_distance_matrix(self.graph.adjacency, all_locs)
            hk_result = held_karp_tsp(dist_matrix, start=0, return_to_start=False)
            optimized_indices = hk_result["optimal_order"]
            optimized_locs = [all_locs[i] for i in optimized_indices if i > 0]
            order["total_distance"] = hk_result["optimal_distance"]
        else:
            optimized_locs = pick_locations
            route_result = multi_stop_dijkstra(self.graph.adjacency, start_pos, pick_locations)
            order["total_distance"] = route_result["distance"]

        order["optimized_route"] = [list(loc) for loc in optimized_locs]

        # Build full path for picker
        home = tuple(picker["home_station"])
        all_stops = optimized_locs + [home]
        full_route = multi_stop_dijkstra(self.graph.adjacency, start_pos, all_stops)

        if not full_route["path"]:
            self._add_event("error", f"No path found for Order #{order['id']}. Resetting picker.")
            picker["status"] = "idle"
            picker["assigned_order_id"] = None
            order["status"] = "pending"
            order["assigned_picker_id"] = None
            return

        # Update picker
        picker["status"] = "traveling"
        picker["assigned_order_id"] = order["id"]
        picker["route"] = [list(p) for p in full_route["path"]]
        picker["route_index"] = 0
        picker["current_target"] = list(optimized_locs[0]) if optimized_locs else list(home)

        self._add_event("assignment", f"Order #{order['id']} -> {picker['name']} (dist: {order['total_distance']:.1f})")

    def _move_pickers(self):
        """Advance each active picker one step along their route."""
        for picker in self.pickers.values():
            if picker["status"] in ("idle",):
                continue
            if not picker["route"] or picker["route_index"] >= len(picker["route"]) - 1:
                continue

            picker["route_index"] += 1
            new_pos = picker["route"][picker["route_index"]]
            picker["current_position"] = list(new_pos)
            picker["total_distance_traveled"] += config.EDGE_WEIGHT_STRAIGHT
            self.total_distance += config.EDGE_WEIGHT_STRAIGHT

            # Track heatmap
            pos_tuple = tuple(new_pos)
            self.heatmap[pos_tuple] = self.heatmap.get(pos_tuple, 0) + 1

            # Update cell visit count in layout
            r, c = new_pos[0], new_pos[1]
            if 0 <= r < self.layout.rows and 0 <= c < self.layout.cols:
                self.layout.grid[r][c]["visit_count"] += 1

    def _check_completions(self):
        """Check if any picker has completed their route."""
        for picker in self.pickers.values():
            if picker["status"] == "idle":
                continue
            if not picker["route"]:
                continue
            if picker["route_index"] >= len(picker["route"]) - 1:
                order_id = picker["assigned_order_id"]
                if order_id and order_id in self.orders:
                    order = self.orders[order_id]
                    order["status"] = "completed"
                    order["completed_at"] = time.time()
                    self.completed_orders.append(order)

                    # Deduct stock
                    for item in order["items"]:
                        pid = item["product_id"]
                        if pid in self.products:
                            self.products[pid]["current_stock"] = max(0, self.products[pid]["current_stock"] - item["quantity"])

                    picker["orders_completed"] += 1
                    self._add_event("completion", f"Order #{order_id} completed by {picker['name']}")

                # Reset picker
                picker["status"] = "idle"
                picker["assigned_order_id"] = None
                picker["route"] = []
                picker["route_index"] = 0
                picker["current_target"] = None

    def _check_replenishment(self):
        """Check stock levels and trigger replenishment tasks."""
        product_list = list(self.products.values())
        new_tasks = self.replenishment.check_stock_levels(product_list, self.graph)
        for task in new_tasks:
            self._add_event("replenishment", f"Replenishing {task['product_name']} (qty: {task['quantity']})")
            # Add stock when task completes (simplified - immediate)
            pid = task["product_id"]
            if pid in self.products:
                self.products[pid]["current_stock"] += task["quantity"]

    def _update_time_tracking(self):
        """Update idle/active time for each picker."""
        for picker in self.pickers.values():
            if picker["status"] == "idle":
                picker["total_idle_time"] += 1
            else:
                picker["total_active_time"] += 1

    def _add_event(self, event_type: str, message: str):
        """Add an event to the log."""
        self.events.append({
            "tick": self.tick_count,
            "time": time.time(),
            "type": event_type,
            "message": message,
        })
        # Keep last 200 events
        if len(self.events) > 200:
            self.events = self.events[-200:]

    def get_state(self) -> dict:
        """Get complete simulation state for broadcasting."""
        return {
            "tick": self.tick_count,
            "running": self.running,
            "paused": self.paused,
            "speed": self.speed,
            "layout": {"rows": self.layout.rows, "cols": self.layout.cols, "grid": self.layout.grid} if self.layout else None,
            "products": self.products,
            "orders": {k: v for k, v in self.orders.items() if v["status"] != "completed"},
            "completed_orders_count": len(self.completed_orders),
            "pickers": self.pickers,
            "events": self.events[-50:],
            "replenishment": self.replenishment.to_serializable(),
            "metrics": self._compute_metrics(),
            "heatmap": {f"{k[0]},{k[1]}": v for k, v in self.heatmap.items()},
        }

    def _compute_metrics(self) -> dict:
        """Compute real-time metrics for the dashboard."""
        active_orders = sum(1 for o in self.orders.values() if o["status"] in ("pending", "assigned", "picking"))
        idle_pickers = sum(1 for p in self.pickers.values() if p["status"] == "idle")

        cycle_times = []
        for o in self.completed_orders[-50:]:
            if o.get("completed_at") and o.get("created_at"):
                ct = o["completed_at"] - o["created_at"]
                if ct > 0:
                    cycle_times.append(ct)

        avg_utilization = 0
        if self.pickers:
            utils = []
            for p in self.pickers.values():
                total = p["total_idle_time"] + p["total_active_time"]
                utils.append((p["total_active_time"] / total * 100) if total > 0 else 0)
            avg_utilization = sum(utils) / len(utils)

        # Shelf utilization
        total_cap = 0
        total_used = 0
        if self.layout:
            for row in self.layout.grid:
                for cell in row:
                    if cell["cell_type"] == CellType.SHELF.value:
                        total_cap += cell["shelf_capacity"]
                        total_used += cell["shelf_used"]

        return {
            "total_distance": round(self.total_distance, 1),
            "active_orders": active_orders,
            "completed_orders": len(self.completed_orders),
            "pending_orders": sum(1 for o in self.orders.values() if o["status"] == "pending"),
            "idle_pickers": idle_pickers,
            "active_pickers": len(self.pickers) - idle_pickers,
            "avg_utilization": round(avg_utilization, 1),
            "avg_cycle_time": round(sum(cycle_times) / len(cycle_times), 2) if cycle_times else 0,
            "shelf_utilization": round((total_used / total_cap * 100) if total_cap > 0 else 0, 1),
            "orders_per_minute": round(len(self.completed_orders) / max(1, self.tick_count) * (1000 / config.SIMULATION_TICK_MS) * 60, 1),
        }
