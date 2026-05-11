"""
Smart Warehouse System — Analytics API Routes
"""
from fastapi import APIRouter

from utils import sanitize_json

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def get_summary():
    """Get KPI summary metrics."""
    from main import simulation_engine
    return sanitize_json({"metrics": simulation_engine._compute_metrics()})


@router.get("/heatmap")
async def get_heatmap():
    """Get cell visit frequency data for heatmap visualization."""
    from main import simulation_engine
    return {"heatmap": simulation_engine.get_state().get("heatmap", {})}


@router.get("/history")
async def get_history():
    """Get time-series metrics from completed orders."""
    from main import simulation_engine

    history = []
    for i, order in enumerate(simulation_engine.completed_orders):
        history.append({
            "order_index": i + 1,
            "cycle_time": round(order.get("completed_at", 0) - order.get("created_at", 0), 2),
            "distance": round(order.get("total_distance", 0), 2),
            "items": sum(item.get("quantity", 1) for item in order.get("items", [])),
        })

    return {"history": history[-100:], "total_completed": len(simulation_engine.completed_orders)}


@router.get("/inventory")
async def get_inventory():
    """Get full product inventory with stock levels."""
    from main import simulation_engine
    products = list(simulation_engine.products.values())
    low_stock = [p for p in products if p.get("current_stock", 0) <= p.get("reorder_threshold", 5)]
    return {
        "products": products,
        "total_products": len(products),
        "low_stock_count": len(low_stock),
        "low_stock_products": low_stock,
    }


@router.get("/pickers")
async def get_picker_stats():
    """Get detailed picker statistics."""
    from main import simulation_engine
    from algorithms.greedy_assignment import calculate_picker_metrics
    metrics = calculate_picker_metrics(list(simulation_engine.pickers.values()), simulation_engine.completed_orders)
    return metrics
