from __future__ import annotations
"""
Smart Warehouse System — Held-Karp Algorithm (Recursive Version)
Optimizes batch picking routes using exact TSP solution.
This version uses sets instead of bitmasks for easier understanding.
"""
import itertools
from typing import Optional, Dict, Tuple, List


def held_karp_tsp(distance_matrix: list[list[float]], start: int = 0, return_to_start: bool = True) -> dict:
    """
    Solve TSP exactly using Recursion + Memoization.
    We use a 'frozenset' to keep track of visited nodes because it's easier to read than bits.
    """
    n = len(distance_matrix)
    
    # Base Case: Nothing to optimize if 1 or 0 locations
    if n <= 1:
        if n == 1:
            optimal_order = [start]
        else:
            optimal_order = []
        return {"optimal_order": optimal_order, "optimal_distance": 0, "dp_table_size": 0}

    # Memoization table: stores (current_node, visited_set) -> (min_distance, next_node)
    memo = {}

    def solve(current: int, visited: frozenset):
        # If we have visited all nodes
        if len(visited) == n:
            if return_to_start:
                # Return distance to the starting point
                return distance_matrix[current][start], start
            else:
                # No return needed, distance is 0
                return 0.0, -1

        # Check if we already solved this specific sub-problem
        state = (current, visited)
        if state in memo:
            return memo[state]

        best_dist = float("inf")
        best_next = -1

        # Try visiting every node that hasn't been visited yet
        for next_node in range(n):
            # Check if next_node is NOT in our visited checklist
            if next_node not in visited:
                # Add next_node to a new checklist
                new_visited = visited | {next_node}
                
                # Recursive call: "Solve the rest of the trip starting from next_node"
                dist_remaining, _ = solve(next_node, new_visited)
                
                # Total distance = (current -> next_node) + (rest of the trip)
                total_dist = distance_matrix[current][next_node] + dist_remaining

                # Keep track of the shortest path found
                if total_dist < best_dist:
                    best_dist = total_dist
                    best_next = next_node

        # Save result in memo table
        memo[state] = (best_dist, best_next)
        return best_dist, best_next

    # Start the recursion with only the starting point visited
    initial_visited = frozenset([start])
    total_distance, _ = solve(start, initial_visited)

    # Reconstruct the path by following the 'best_next' choices we saved
    optimal_order = [start]
    current_node = start
    current_visited = initial_visited

    while len(current_visited) < n:
        _, next_node = memo[(current_node, current_visited)]
        optimal_order.append(next_node)
        current_visited |= {next_node}
        current_node = next_node

    # If returning to start, add start to the end of the order list for the UI
    if return_to_start:
        optimal_order.append(start)

    return {
        "optimal_order": optimal_order,
        "optimal_distance": round(total_distance, 2),
        "dp_table_size": len(memo),
        "label": "Held-Karp (Recursive DP)"
    }


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
            if c not in visited:
                if distance_matrix[current][c] < best_dist:
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
        order.append(start)

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
        if i != -1: # Filter out dummy values
            optimal_labels.append(location_labels[i])

    greedy_labels = []
    for i in greedy["order"]:
        greedy_labels.append(location_labels[i])

    return {
        "optimal": {
            "order": optimal["optimal_order"], 
            "order_labels": optimal_labels, 
            "distance": optimal["optimal_distance"], 
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
