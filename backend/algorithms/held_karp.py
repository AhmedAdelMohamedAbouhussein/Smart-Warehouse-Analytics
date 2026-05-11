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
    n = len(distance_matrix)
    if n <= 1:
        return {"optimal_order": [start] if n == 1 else [], "optimal_distance": 0, "dp_table_size": 0, "dp_states": []}
    if n == 2:
        other = 1 - start
        d = distance_matrix[start][other] + (distance_matrix[other][start] if return_to_start else 0)
        return {"optimal_order": [start, other], "optimal_distance": d, "dp_table_size": 2, "dp_states": []}

    dp = {}
    parent = {}
    dp_states_log = []
    start_mask = 1 << start

    # Base case: go from start to each other node
    for i in range(n):
        if i == start:
            continue
        mask = start_mask | (1 << i)
        dp[(mask, i)] = distance_matrix[start][i]
        parent[(mask, i)] = start

    # Iterate over subset sizes 3..n
    for subset_size in range(3, n + 1):
        other_nodes = [i for i in range(n) if i != start]
        for subset in itertools.combinations(other_nodes, subset_size - 1):
            mask = start_mask
            for node in subset:
                mask |= (1 << node)
            for end in subset:
                prev_mask = mask & ~(1 << end)
                best_cost = float("inf")
                best_prev = -1
                for prev in subset:
                    if prev == end:
                        continue
                    prev_cost = dp.get((prev_mask, prev), float("inf"))
                    if prev_cost == float("inf"):
                        continue
                    total = prev_cost + distance_matrix[prev][end]
                    if total < best_cost:
                        best_cost = total
                        best_prev = prev
                if best_cost < float("inf"):
                    dp[(mask, end)] = best_cost
                    parent[(mask, end)] = best_prev
        dp_states_log.append({"subset_size": subset_size, "states_computed": len(dp)})

    # Find optimal tour
    full_mask = (1 << n) - 1
    best_distance = float("inf")
    best_last = -1
    for last in range(n):
        if last == start:
            continue
        cost = dp.get((full_mask, last), float("inf"))
        if return_to_start:
            cost += distance_matrix[last][start]
        if cost < best_distance:
            best_distance = cost
            best_last = last

    if best_last == -1:
        return {"optimal_order": list(range(n)), "optimal_distance": float("inf"), "dp_table_size": len(dp), "dp_states": dp_states_log}

    # Reconstruct path
    path = []
    mask = full_mask
    current = best_last
    while current != start:
        path.append(current)
        prev = parent.get((mask, current))
        if prev is None:
            break
        mask = mask & ~(1 << current)
        current = prev
    path.append(start)
    path.reverse()

    return {"optimal_order": path, "optimal_distance": round(best_distance, 2), "dp_table_size": len(dp), "dp_states": dp_states_log}


def greedy_nearest_neighbor(distance_matrix: list[list[float]], start: int = 0, return_to_start: bool = True) -> dict:
    """Greedy nearest-neighbor TSP heuristic for comparison."""
    n = len(distance_matrix)
    if n <= 1:
        return {"order": [start] if n == 1 else [], "distance": 0, "label": "Greedy Nearest Neighbor"}

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
        location_labels = [f"Loc {i}" for i in range(n)]

    optimal = held_karp_tsp(distance_matrix, start, return_to_start)
    greedy = greedy_nearest_neighbor(distance_matrix, start, return_to_start)

    improvement = 0.0
    if greedy["distance"] > 0:
        improvement = round(((greedy["distance"] - optimal["optimal_distance"]) / greedy["distance"]) * 100, 2)

    return {
        "optimal": {"order": optimal["optimal_order"], "order_labels": [location_labels[i] for i in optimal["optimal_order"]], "distance": optimal["optimal_distance"], "dp_states_computed": optimal["dp_table_size"], "label": "Held-Karp DP (Optimal)"},
        "greedy": {"order": greedy["order"], "order_labels": [location_labels[i] for i in greedy["order"]], "distance": greedy["distance"], "label": "Greedy Nearest Neighbor"},
        "improvement_pct": improvement,
        "locations": location_labels,
        "distance_matrix": distance_matrix,
    }
