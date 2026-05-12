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
        if isinstance(picker, dict):
            status = picker.get("status")
            raw_pos = picker.get("current_position", (0, 0))
        else:
            status = getattr(picker, "status", None)
            raw_pos = getattr(picker, "current_position", (0, 0))
            
        # Step 2: Decide if picker is available
        # They must be in 'idle' status, unless we are in a demo mode that ignores status
        is_available = (status == "idle" or ignore_busy)
        pos = tuple(raw_pos)

        # Step 3: Calculate distance from picker's current position to the item
        if is_available:
            dist = distance_func(pos, first_location)
        else:
            # If busy, we treat them as infinitely far away so they aren't picked
            dist = float("inf")

        if dist != float("inf"):
            rounded_dist = round(dist, 2)
        else:
            rounded_dist = None

        picker_distances.append({
            "picker_id": picker["id"],
            "picker_name": picker.get("name", f"Picker {picker['id']}"),
            "distance": rounded_dist,
            "available": is_available,
            "position": pos,
        })

        if is_available and dist < best_distance:
            best_distance = dist
            best_picker_id = picker["id"]

    if best_picker_id is None:
        reason = "No pickers in system"
    else:
        reason = f"Nearest idle picker (distance: {best_distance:.1f})"

    if ignore_busy and best_picker_id is not None:
        reason = f"Closest Picker (Lab Demo): {best_distance:.1f}m"

    if best_distance != float("inf"):
        final_dist = round(best_distance, 2)
    else:
        final_dist = None

    return {
        "assigned_picker_id": best_picker_id,
        "distance_to_first_item": final_dist,
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
        if total_t > 0:
            utilization = (active_t / total_t * 100)
        else:
            utilization = 0.0

        # Orders completed by this picker
        picker_orders = []
        for o in completed_orders:
            if o.get("assigned_picker_id") == pid:
                picker_orders.append(o)
        
        total_dist = picker.get("total_distance_traveled", 0)
        if picker_orders:
            avg_dist = total_dist / len(picker_orders)
        else:
            avg_dist = 0

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

    if pickers:
        avg_util = round(total_util / len(pickers), 1)
    else:
        avg_util = 0

    if cycle_times:
        avg_cycle = round(sum(cycle_times) / len(cycle_times), 2)
    else:
        avg_cycle = 0

    result = {
        "per_picker": per_picker,
        "overall": {
            "avg_utilization": avg_util,
            "total_orders_completed": len(completed_orders),
            "avg_cycle_time": avg_cycle,
            "total_distance": 0.0,
        },
    }
    
    # Calculate total distance separately to avoid generator expression
    total_dist_all = 0.0
    for p in pickers:
        total_dist_all += p.get("total_distance_traveled", 0)
    
    result["overall"]["total_distance"] = round(total_dist_all, 1)
    return result
