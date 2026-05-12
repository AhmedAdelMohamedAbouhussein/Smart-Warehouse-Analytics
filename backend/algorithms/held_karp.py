from __future__ import annotations
"""
Smart Warehouse System — Held-Karp Algorithm (DP TSP)
Optimizes batch picking routes using exact TSP solution.
Complexity: O(n² × 2ⁿ) time, O(n × 2ⁿ) space. Practical for n ≤ 20.
"""
import itertools
from typing import Optional


def held_karp_tsp(distance_matrix: list[list[float]], start: int = 0, return_to_start: bool = True) -> dict:
    """
    Solve TSP exactly using Held-Karp DP with bitmask subsets.
    dp[(mask, i)] = min cost to reach node i having visited exactly the nodes in mask.
    """
    # n is the number of locations to visit
    n = len(distance_matrix)
    
    # Base Case: 0 or 1 locations (Nothing to optimize)
    if n <= 1:
        if n == 1:
            optimal_order = [start]
        else:
            optimal_order = []
        return {"optimal_order": optimal_order, "optimal_distance": 0, "dp_table_size": 0, "dp_states": []}
        
    # Case: Exactly 2 locations (Start and one destination)
    if n == 2:
        # Trick: If start is 0, other is 1. If start is 1, other is 0.
        other = 1 - start
        
        # Total distance is start -> other
        dist_to_other = distance_matrix[start][other]
        
        # If we must return to start, add other -> start distance
        if return_to_start:
            d = dist_to_other + distance_matrix[other][start]
        else:
            d = dist_to_other
            
        return {"optimal_order": [start, other], "optimal_distance": d, "dp_table_size": 2, "dp_states": []}

    # --- START OF MAIN HELD-KARP ALGORITHM ---
    
    # dp table: stores the minimum cost to reach node 'i' having visited the set of nodes in 'mask'
    # Key: (mask, last_node), Value: shortest distance
    dp = {}
    
    # parent table: stores the 'previous' node so we can reconstruct the path at the end
    parent = {}
    
    dp_states_log = []
    
    # Bitmask for the starting location (e.g., if start is 0, start_mask is 1 / '0001')
    start_mask = 1 << start

    # Step 1: Initialize trips of size 2 (Start -> Each other node)
    for i in range(n):
        if i == start:
            continue
        # Create a checklist with [Start] and [Item i] checked
        mask = start_mask | (1 << i)
        
        # Distance is just the direct line from Start to i
        dp[(mask, i)] = distance_matrix[start][i]
        
        # Record that we came from 'start' to get to 'i'
        parent[(mask, i)] = start

    # Step 2: Iterate over subset sizes from 3 up to N
    # This is the "Building Up" phase of Dynamic Programming
    for subset_size in range(3, n + 1):
        # Find all nodes that are NOT the starting point
        other_nodes = []
        for i in range(n):
            if i != start:
                other_nodes.append(i)
        
        # Generate EVERY possible combination of items for this subset size
        # This ensures we check every possible group of items
        for subset in itertools.combinations(other_nodes, subset_size - 1):
            
            # Convert the list of items into a single Bitmask number (Checklist)
            mask = start_mask
            for node in subset:
                mask |= (1 << node)
            
            # Now, pick one item from the group to be the "Last" stop (end)
            for end in subset:
                # Find the mask of the group BEFORE we added 'end'
                # (We use ~ and & to uncheck the box for 'end')
                prev_mask = mask & ~(1 << end)
                
                best_cost = float("inf")
                best_prev = -1
                
                # Check every OTHER item in the group to see which one was the best second-to-last stop
                for prev in subset:
                    if prev == end:
                        continue
                    
                    # Look up the shortest path to 'prev' from our DP table (Memoization)
                    prev_cost = dp.get((prev_mask, prev), float("inf"))
                    
                    if prev_cost == float("inf"):
                        continue
                    
                    # Potential total cost: (Path to prev) + (prev -> end)
                    total = prev_cost + distance_matrix[prev][end]
                    
                    # If this is the shortest we've found for this group, save it
                    if total < best_cost:
                        best_cost = total
                        best_prev = prev
                
                # Write the winner into our DP memory
                if best_cost < float("inf"):
                    dp[(mask, end)] = best_cost
                    parent[(mask, end)] = best_prev
                    
        dp_states_log.append({"subset_size": subset_size, "states_computed": len(dp)})

    # Step 3: Find the Optimal Finishing Point
    # We look at the full group (all items visited) and see which end point is best
    full_mask = (1 << n) - 1
    best_distance = float("inf")
    best_last = -1
    
    for last in range(n):
        if last == start:
            continue
            
        cost = dp.get((full_mask, last), float("inf"))
        
        # If we need to return to start, add that final leg
        if return_to_start:
            cost += distance_matrix[last][start]
            
        if cost < best_distance:
            best_distance = cost
            best_last = last

    # If no path was found (disconnected graph)
    if best_last == -1:
        return {"optimal_order": list(range(n)), "optimal_distance": float("inf"), "dp_table_size": len(dp), "dp_states": dp_states_log}

    # Step 4: Path Reconstruction (Trace Backwards)
    # We work from the end to the start using our 'parent' map
    path = []
    mask = full_mask
    current = best_last
    
    while current != start:
        path.append(current)
        # Look up who came before 'current' in the shortest path
        prev = parent.get((mask, current))
        if prev is None:
            break
        # Uncheck 'current' and move to the parent
        mask = mask & ~(1 << current)
        current = prev
    
    path.append(start)
    path.reverse() # Flip the path so it starts at 'start'

    return {"optimal_order": path, "optimal_distance": round(best_distance, 2), "dp_table_size": len(dp), "dp_states": dp_states_log}


def greedy_nearest_neighbor(distance_matrix: list[list[float]], start: int = 0, return_to_start: bool = True) -> dict:
    """Greedy nearest-neighbor TSP heuristic for comparison."""
    n = len(distance_matrix)
    if n <= 1:
        if n == 1:
            order_list = [start]
        else:
            order_list = []
        return {"order": order_list, "distance": 0, "label": "Greedy Nearest Neighbor"}

    visited = {start}
    order = [start]
    total_distance = 0.0
    current = start

    while len(visited) < n:
        best_next, best_dist = -1, float("inf")
        for c in range(n):
            if c not in visited and distance_matrix[current][c] < best_dist:
                best_dist = distance_matrix[current][c]
                best_next = c
        if best_next == -1:
            break
        visited.add(best_next)
        order.append(best_next)
        total_distance += best_dist
        current = best_next

    if return_to_start:
        total_distance += distance_matrix[current][start]

    return {"order": order, "distance": round(total_distance, 2), "label": "Greedy Nearest Neighbor"}


def compare_pick_routes(distance_matrix: list[list[float]], location_labels: Optional[list[str]] = None, start: int = 0, return_to_start: bool = True) -> dict:
    """Run both Held-Karp (optimal) and Greedy NN, return side-by-side comparison."""
    n = len(distance_matrix)
    if location_labels is None:
        location_labels = []
        for i in range(n):
            location_labels.append(f"Loc {i}")

    optimal = held_karp_tsp(distance_matrix, start, return_to_start)
    greedy = greedy_nearest_neighbor(distance_matrix, start, return_to_start)

    improvement = 0.0
    if greedy["distance"] > 0:
        improvement = round(((greedy["distance"] - optimal["optimal_distance"]) / greedy["distance"]) * 100, 2)

    optimal_labels = []
    for i in optimal["optimal_order"]:
        optimal_labels.append(location_labels[i])

    greedy_labels = []
    for i in greedy["order"]:
        greedy_labels.append(location_labels[i])

    return {
        "optimal": {
            "order": optimal["optimal_order"], 
            "order_labels": optimal_labels, 
            "distance": optimal["optimal_distance"], 
            "dp_states_computed": optimal["dp_table_size"], 
            "label": "Held-Karp DP (Optimal)"
        },
        "greedy": {
            "order": greedy["order"], 
            "order_labels": greedy_labels, 
            "distance": greedy["distance"], 
            "label": "Greedy Nearest Neighbor"
        },
        "improvement_pct": improvement,
        "locations": location_labels,
        "distance_matrix": distance_matrix,
    }
