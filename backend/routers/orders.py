"""
Smart Warehouse System — Orders API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/orders", tags=["orders"])


class CreateOrderRequest(BaseModel):
    items: list[dict] = []  # [{product_id, quantity}]


@router.get("/")
async def list_orders(status: Optional[str] = None):
    """List all orders, optionally filtered by status."""
    from main import simulation_engine
    orders = list(simulation_engine.orders.values())
    if status:
        orders = [o for o in orders if o["status"] == status]
    completed = simulation_engine.completed_orders[-50:]
    return {
        "active_orders": orders,
        "completed_orders": completed,
        "total_active": len(orders),
        "total_completed": len(simulation_engine.completed_orders),
    }


@router.get("/{order_id}")
async def get_order(order_id: int):
    """Get order details with pick route."""
    from main import simulation_engine
    order = simulation_engine.orders.get(order_id)
    if not order:
        for o in simulation_engine.completed_orders:
            if o["id"] == order_id:
                order = o
                break
    if not order:
        return {"error": "Order not found"}
    return {"order": order}


@router.post("/")
async def create_order(req: CreateOrderRequest):
    """Manually create a new order."""
    from main import simulation_engine
    items = []
    for item_req in req.items:
        pid = item_req.get("product_id")
        qty = item_req.get("quantity", 1)
        if pid in simulation_engine.products:
            product = simulation_engine.products[pid]
            items.append({
                "product_id": pid,
                "product_name": product["name"],
                "quantity": qty,
                "shelf_location": product.get("shelf_location"),
            })
    if not items:
        return {"error": "No valid items"}

    import time
    order_id = max((o["id"] for o in simulation_engine.orders.values()), default=0) + 1
    order_id = max(order_id, simulation_engine.order_generator.order_id_counter)
    simulation_engine.order_generator.order_id_counter = order_id + 1

    order = {
        "id": order_id, "status": "pending", "items": items,
        "assigned_picker_id": None, "created_at": time.time(),
        "assigned_at": None, "completed_at": None,
        "total_distance": 0.0, "pick_route": [], "optimized_route": [],
    }
    simulation_engine.orders[order_id] = order
    return {"order": order}
