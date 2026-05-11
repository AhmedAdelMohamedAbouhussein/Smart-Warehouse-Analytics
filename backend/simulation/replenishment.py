"""
Smart Warehouse System — Replenishment Subsystem
Monitors stock levels and schedules stock replenishment tasks.
"""
from __future__ import annotations
import time
import config


class ReplenishmentManager:
    """Monitors stock levels and generates replenishment tasks."""

    def __init__(self):
        self.active_tasks: list[dict] = []
        self.completed_tasks: list[dict] = []
        self.task_id_counter = 1

    def check_stock_levels(self, products: list[dict], warehouse_graph) -> list[dict]:
        """
        Check all products and generate replenishment tasks for low stock.

        Args:
            products: List of product dicts with current_stock and reorder_threshold
            warehouse_graph: WarehouseGraph instance for routing

        Returns:
            List of new replenishment tasks generated
        """
        new_tasks = []

        for product in products:
            pid = product["id"]
            stock = product.get("current_stock", 0)
            threshold = product.get("reorder_threshold", config.DEFAULT_REORDER_THRESHOLD)

            # Skip if already has an active replenishment task
            if any(t["product_id"] == pid and t["status"] == "active" for t in self.active_tasks):
                continue

            if stock <= threshold:
                task = self._create_task(product, warehouse_graph)
                if task:
                    self.active_tasks.append(task)
                    new_tasks.append(task)

        return new_tasks

    def _create_task(self, product: dict, warehouse_graph) -> dict | None:
        """Create a replenishment task for a product."""
        shelf_loc = product.get("shelf_location")
        if not shelf_loc:
            return None

        # Source: receiving dock (top of warehouse)
        source = (0, 1)  # First receiving dock cell
        # Destination: product's shelf access point
        dest = warehouse_graph.get_location_for_cell(shelf_loc[0], shelf_loc[1])
        if not dest:
            return None

        # Calculate route
        from algorithms.dijkstra import dijkstra
        route_result = dijkstra(warehouse_graph.adjacency, source, dest)

        task = {
            "id": self.task_id_counter,
            "product_id": product["id"],
            "product_name": product.get("name", ""),
            "status": "active",
            "source": source,
            "destination": dest,
            "shelf_location": shelf_loc,
            "quantity": config.REPLENISHMENT_QUANTITY,
            "route": route_result["path"],
            "route_index": 0,
            "distance": route_result["distance"],
            "created_at": time.time(),
            "completed_at": None,
        }
        self.task_id_counter += 1
        return task

    def advance_tasks(self) -> list[dict]:
        """Advance all active replenishment tasks by one step. Returns completed tasks."""
        completed = []
        for task in self.active_tasks:
            if task["status"] != "active":
                continue
            task["route_index"] += 1
            if task["route_index"] >= len(task["route"]):
                task["status"] = "completed"
                task["completed_at"] = time.time()
                completed.append(task)

        # Move completed tasks
        for t in completed:
            self.active_tasks.remove(t)
            self.completed_tasks.append(t)

        return completed

    def get_active_positions(self) -> list[dict]:
        """Get current positions of all active replenishment carts."""
        positions = []
        for task in self.active_tasks:
            if task["route"] and task["route_index"] < len(task["route"]):
                positions.append({
                    "task_id": task["id"],
                    "product_name": task["product_name"],
                    "position": task["route"][task["route_index"]],
                    "destination": task["destination"],
                })
        return positions

    def to_serializable(self) -> dict:
        """Serialize for API/WebSocket."""
        return {
            "active_tasks": [{**t, "source": list(t["source"]), "destination": list(t["destination"]),
                              "route": [list(r) for r in t["route"]], "shelf_location": list(t["shelf_location"])}
                             for t in self.active_tasks],
            "completed_count": len(self.completed_tasks),
            "total_quantity_moved": sum(t["quantity"] for t in self.completed_tasks),
            "total_distance": round(sum(t["distance"] for t in self.completed_tasks if t["distance"] != float("inf")), 1),
        }
