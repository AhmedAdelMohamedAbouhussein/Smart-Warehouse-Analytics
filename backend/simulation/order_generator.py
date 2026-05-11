"""
Smart Warehouse System — Order Generator
Simulates realistic customer order arrivals using Poisson distribution.
"""
from __future__ import annotations
import random
import math
from typing import Optional
import config


class OrderGenerator:
    """Generates simulated customer orders based on product demand frequencies."""

    def __init__(self, products: list[dict], arrival_rate: float = config.ORDER_ARRIVAL_RATE):
        self.products = products
        self.arrival_rate = arrival_rate
        self.order_id_counter = 1
        self._build_demand_weights()

    def _build_demand_weights(self):
        """Build weighted selection based on demand frequency."""
        self.product_weights = []
        self.product_ids = []
        for p in self.products:
            freq = p.get("demand_frequency", 1.0)
            self.product_weights.append(max(freq, 0.01))
            self.product_ids.append(p["id"])

    def update_products(self, products: list[dict]):
        """Update product catalog."""
        self.products = products
        self._build_demand_weights()

    def should_generate(self) -> bool:
        """Determine if an order should be generated this tick (Poisson process)."""
        return random.random() < self.arrival_rate

    def generate_order(self, products_map: dict) -> Optional[dict]:
        """
        Generate a single random order.

        Args:
            products_map: {product_id: product_dict} for looking up details

        Returns:
            Order dict or None if generation conditions not met
        """
        if not self.product_ids:
            return None

        num_items = random.randint(config.MIN_ITEMS_PER_ORDER, config.MAX_ITEMS_PER_ORDER)
        num_items = min(num_items, len(self.product_ids))

        # Select products weighted by demand frequency
        selected_ids = []
        available_indices = list(range(len(self.product_ids)))
        available_weights = list(self.product_weights)

        for _ in range(num_items):
            if not available_indices:
                break
            chosen_idx = random.choices(available_indices, weights=available_weights, k=1)[0]
            pos = available_indices.index(chosen_idx)
            selected_ids.append(self.product_ids[chosen_idx])
            available_indices.pop(pos)
            available_weights.pop(pos)

        # Build order items
        items = []
        for pid in selected_ids:
            product = products_map.get(pid)
            if product and product.get("current_stock", 0) > 0:
                qty = random.randint(1, min(3, product.get("current_stock", 1)))
                items.append({
                    "product_id": pid,
                    "product_name": product.get("name", f"Product {pid}"),
                    "quantity": qty,
                    "shelf_location": product.get("shelf_location"),
                })

        if not items:
            return None

        import time
        order = {
            "id": self.order_id_counter,
            "status": "pending",
            "items": items,
            "assigned_picker_id": None,
            "created_at": time.time(),
            "assigned_at": None,
            "completed_at": None,
            "total_distance": 0.0,
            "pick_route": [],
            "optimized_route": [],
        }
        self.order_id_counter += 1
        return order
