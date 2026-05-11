from __future__ import annotations
"""
Smart Warehouse System — Greedy Real-Time Order Assignment
Assigns incoming orders to the nearest available picker.
Complexity: O(P) per assignment where P = number of pickers.
"""
from typing import Optional


def assign_order_greedy(order: dict, pickers: list[dict], distance_func, ignore_busy: bool = False) -> dict:
    """
    Assign an order to the nearest available (idle) picker.
    If ignore_busy is True, considers all pickers regardless of status.
    """
    # Get first pick location from order
    pick_locations = []
    for item in order.get("items", []):
        loc = item.get("shelf_location")
        if loc:
            pick_locations.append(tuple(loc))

    if not pick_locations:
        return {"assigned_picker_id": None, "distance_to_first_item": 0, "picker_distances": [], "assignment_reason": "No pick locations"}

    first_location = pick_locations[0]

    # Calculate distance from each picker to the first pick location
    picker_distances = []
    best_picker_id = None
    best_distance = float("inf")

    for picker in pickers:
        # Support both dict and object access
        status = picker.get("status") if isinstance(picker, dict) else getattr(picker, "status", None)
        is_available = status == "idle" or ignore_busy
        
        raw_pos = picker.get("current_position", (0, 0)) if isinstance(picker, dict) else getattr(picker, "current_position", (0, 0))
        pos = tuple(raw_pos)
        dist = distance_func(pos, first_location) if is_available else float("inf")

        picker_distances.append({
            "picker_id": picker["id"],
            "picker_name": picker.get("name", f"Picker {picker['id']}"),
            "distance": round(dist, 2) if dist != float("inf") else None,
            "available": is_available,
            "position": pos,
        })

        if is_available and dist < best_distance:
            best_distance = dist
            best_picker_id = picker["id"]

    reason = "No pickers in system" if best_picker_id is None else f"Nearest idle picker (distance: {best_distance:.1f})"
    if ignore_busy and best_picker_id is not None:
        reason = f"Closest Picker (Lab Demo): {best_distance:.1f}m"

    return {
        "assigned_picker_id": best_picker_id,
        "distance_to_first_item": round(best_distance, 2) if best_distance != float("inf") else None,
        "picker_distances": picker_distances,
        "assignment_reason": reason,
    }


def calculate_picker_metrics(pickers: list[dict], completed_orders: list[dict]) -> dict:
    """
    Compute picker performance metrics.

    Returns:
        {
            "per_picker": [{id, name, utilization, orders_completed, avg_distance, total_distance}, ...],
            "overall": {avg_utilization, total_orders, avg_cycle_time, total_distance},
        }
    """
    per_picker = []
    total_util = 0.0

    for picker in pickers:
        pid = picker["id"]
        idle_t = picker.get("total_idle_time", 0)
        active_t = picker.get("total_active_time", 0)
        total_t = idle_t + active_t
        utilization = (active_t / total_t * 100) if total_t > 0 else 0.0

        # Orders completed by this picker
        picker_orders = [o for o in completed_orders if o.get("assigned_picker_id") == pid]
        total_dist = picker.get("total_distance_traveled", 0)
        avg_dist = total_dist / len(picker_orders) if picker_orders else 0

        per_picker.append({
            "id": pid,
            "name": picker.get("name", f"Picker {pid}"),
            "utilization": round(utilization, 1),
            "orders_completed": len(picker_orders),
            "avg_distance_per_order": round(avg_dist, 1),
            "total_distance": round(total_dist, 1),
            "status": picker.get("status", "idle"),
        })
        total_util += utilization

    # Overall metrics
    cycle_times = []
    for o in completed_orders:
        ct = o.get("completed_at", 0) - o.get("created_at", 0)
        if ct > 0:
            cycle_times.append(ct)

    return {
        "per_picker": per_picker,
        "overall": {
            "avg_utilization": round(total_util / len(pickers), 1) if pickers else 0,
            "total_orders_completed": len(completed_orders),
            "avg_cycle_time": round(sum(cycle_times) / len(cycle_times), 2) if cycle_times else 0,
            "total_distance": round(sum(p.get("total_distance_traveled", 0) for p in pickers), 1),
        },
    }
