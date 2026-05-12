from __future__ import annotations

"""
Smart Warehouse System — Bin Packing Algorithm (Slotting Optimization)
Optimizes warehouse storage allocation using First Fit Decreasing + ABC classification.

Algorithms:
    - ABC Velocity Classification: Rank products by demand frequency
    - First Fit Decreasing (FFD): Pack items into bins efficiently
    - Zone-Based Slotting: Place high-velocity items near pick stations

Complexity:
    - ABC Classification: O(n log n) for sorting
    - FFD: O(n × m) where n = items, m = bins
"""

from typing import Optional
import config


def abc_classify(products: list[dict]) -> dict[str, list[dict]]:
    """
    Classify products into A/B/C categories based on rank (position in sorted list).

    - Class A → top 20% of products (highest demand)
    - Class B → next 30% of products
    - Class C → remaining 50% of products
    """
    if not products:
        return {"A": [], "B": [], "C": [], "classification_details": []}

    # --- STEP 1: RANK-BASED SORTING ---
    # We sort products by demand frequency (popularity) in descending order.
    # The most popular items (High Velocity) go to the top of the list.
    sorted_products = sorted(products, key=lambda p: p.get("demand_frequency", 0), reverse=True)
    n = len(sorted_products)

    # --- STEP 2: CALCULATE SPLIT POINTS (20/30/50 Rule) ---
    # Class A: Top 20% of products (High Velocity - The "Rockstars")
    # Class B: Next 30% of products (Medium Velocity)
    # Class C: Remaining 50% of products (Low Velocity - Slow Movers)
    a_count = max(1, int(n * 0.2))
    b_count = max(1, int(n * 0.3))

    # Boundary handling for small lists
    if a_count >= n:
        a_count = n
        b_count = 0
    elif a_count + b_count > n:
        b_count = n - a_count

    a_end = a_count
    b_end = a_count + b_count

    result = {"A": [], "B": [], "C": [], "classification_details": []}

    for i in range(n):
        product = sorted_products[i]
        if i < a_end:
            velocity_class = "A"
        elif i < b_end:
            velocity_class = "B"
        else:
            velocity_class = "C"

        # Create classified version
        classified_product = product.copy()
        classified_product["velocity_class"] = velocity_class
        
        result[velocity_class].append(classified_product)

        # Build flat details list
        result["classification_details"].append({
            "id": product.get("id"),
            "name": product.get("name", ""),
            "demand_frequency": product.get("demand_frequency", 0),
            "velocity_class": velocity_class,
        })

    return result


def first_fit_decreasing(
    items: list[dict],
    bins: list[dict],
) -> dict:
    """
    First Fit Decreasing bin packing algorithm.

    Sorts items by volume (descending), then places each item into the
    first bin that has enough remaining capacity.

    Args:
        items: List of {id, volume, ...} dicts
        bins: List of {id, capacity, row, col, zone, ...} dicts

    Returns:
        {
            "placements": {item_id: bin_id, ...},
            "bin_utilization": {bin_id: {capacity, used, utilization_pct}, ...},
            "unplaced_items": [item_ids...],
            "total_bins_used": int,
            "avg_utilization": float,
            "steps": [{action, item_id, bin_id, ...}, ...]  # For visualization
        }
    """
    # --- STEP 1: SORT ITEMS BY VOLUME (DECREASING) ---
    # This is the "Decreasing" part of First-Fit Decreasing (FFD).
    # We pack the biggest items first to ensure they don't get stuck at the end.
    sorted_items = sorted(items, key=lambda x: x.get("volume", 0), reverse=True)

    # Track bin remaining capacity
    capacities = {}
    for b in bins:
        capacities[b["id"]] = b.get("capacity", config.SHELF_CAPACITY)

    bin_capacity = capacities.copy()
    bin_remaining = capacities.copy()

    placements = {}
    unplaced = []
    steps = []  # Animation steps for visualization

    for item in sorted_items:
        item_id = item["id"]
        item_volume = item.get("volume", 1.0)
        placed = False

        # Step 2: Try each bin in order (First Fit)
        # We pick the very first bin that can fit the item's volume
        for b in bins:
            bin_id = b["id"]
            if bin_remaining[bin_id] >= item_volume:
                # Place item in this bin
                placements[item_id] = bin_id
                bin_remaining[bin_id] -= item_volume
                placed = True

                steps.append({
                    "action": "place",
                    "item_id": item_id,
                    "item_name": item.get("name", ""),
                    "item_volume": item_volume,
                    "bin_id": bin_id,
                    "bin_remaining": bin_remaining[bin_id],
                    "bin_location": (b.get("row", 0), b.get("col", 0)),
                })
                break
            else:
                steps.append({
                    "action": "skip",
                    "item_id": item_id,
                    "bin_id": bin_id,
                    "reason": f"Insufficient capacity ({bin_remaining[bin_id]:.1f} < {item_volume:.1f})",
                })

        if not placed:
            unplaced.append(item_id)
            steps.append({
                "action": "unplaced",
                "item_id": item_id,
                "item_volume": item_volume,
                "reason": "No bin with sufficient capacity",
            })

    # Calculate utilization metrics
    bins_used = set(placements.values())
    bin_utilization = {}
    for b in bins:
        bid = b["id"]
        cap = bin_capacity[bid]
        used = cap - bin_remaining[bid]
        
        if cap > 0:
            util_pct = round((used / cap) * 100, 2)
        else:
            util_pct = 0
            
        bin_utilization[bid] = {
            "capacity": cap,
            "used": round(used, 2),
            "utilization_pct": util_pct,
        }

    used_bins = []
    for bid, bu in bin_utilization.items():
        if bu["used"] > 0:
            used_bins.append(bu)

    total_util = 0.0
    for bu in used_bins:
        total_util += bu["utilization_pct"]
    
    if used_bins:
        avg_util = total_util / len(used_bins)
    else:
        avg_util = 0

    return {
        "placements": placements,
        "bin_utilization": bin_utilization,
        "unplaced_items": unplaced,
        "total_bins_used": len(bins_used),
        "avg_utilization": round(avg_util, 2),
        "steps": steps,
    }


def optimize_slotting(
    products: list[dict],
    shelves: list[dict],
) -> dict:
    """
    Full slotting optimization pipeline:
    1. ABC classify products by demand frequency
    2. Map ABC zones to warehouse shelf zones
    3. FFD pack products into zone-appropriate shelves

    Args:
        products: List of product dicts
        shelves: List of shelf dicts with zone, capacity, row, col

    Returns:
        {
            "classification": ABC result,
            "placements": {product_id: shelf_id},
            "zone_assignments": {zone: [product_ids]},
            "metrics": {utilization, bins_used, unplaced},
            "steps": [...],  # Visualization steps
        }
    """
    # Step 1: ABC classification
    classification = abc_classify(products)

    # Step 2: Group shelves by zone
    zone_shelves = {"A": [], "B": [], "C": []}
    for shelf in shelves:
        zone = shelf.get("zone", "C")
        if zone in zone_shelves:
            zone_shelves[zone].append(shelf)

    # Step 3: FFD pack each zone separately
    all_placements = {}
    all_steps = []
    zone_metrics = {}

    for zone in ["A", "B", "C"]:
        zone_products = classification[zone]
        zone_bins = zone_shelves.get(zone, [])

        if not zone_products or not zone_bins:
            zone_metrics[zone] = {"products": 0, "bins_used": 0, "avg_utilization": 0}
            continue

        # Prepare items with volume
        items = []
        for p in zone_products:
            vol = p.get("width", 1) * p.get("height", 1) * p.get("depth", 1)
            items.append({**p, "volume": vol})

        result = first_fit_decreasing(items, zone_bins)

        all_placements.update(result["placements"])
        for step in result["steps"]:
            step["zone"] = zone
        all_steps.extend(result["steps"])

        zone_metrics[zone] = {
            "products": len(zone_products),
            "bins_used": result["total_bins_used"],
            "avg_utilization": result["avg_utilization"],
            "unplaced": len(result["unplaced_items"]),
        }

    return {
        "classification": {
            "A": len(classification["A"]),
            "B": len(classification["B"]),
            "C": len(classification["C"]),
            "details": classification["classification_details"],
        },
        "placements": all_placements,
        "zone_metrics": zone_metrics,
        "steps": all_steps,
        "total_products_placed": len(all_placements),
        "total_products": len(products),
    }
