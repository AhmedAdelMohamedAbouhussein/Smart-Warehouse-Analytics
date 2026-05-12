from __future__ import annotations
"""
Smart Warehouse System — Dijkstra's Algorithm
Computes shortest picking routes and optimizes picker travel paths.

Algorithm: Dijkstra's single-source shortest path
Complexity: O((V + E) log V) with a min-heap priority queue
"""

import heapq
from typing import Optional


def dijkstra(
    graph: dict[tuple[int, int], list[tuple[tuple[int, int], float]]],
    source: tuple[int, int],
    target: tuple[int, int],
) -> dict:
    """
    Compute shortest path from source to target on a warehouse graph.

    Args:
        graph: Adjacency list {node: [(neighbor, weight), ...]}
        source: Starting node (row, col)
        target: Destination node (row, col)

    Returns:
        {
            "path": [(r,c), ...],          # Shortest path nodes
            "distance": float,              # Total distance
            "explored": [(r,c), ...],       # Nodes explored in order (for visualization)
            "explored_edges": [((r1,c1),(r2,c2)), ...],  # Edges explored
        }
    """
    if source not in graph:
        return {"path": [], "distance": float("inf"), "explored": [], "explored_edges": []}
    if source == target:
        return {"path": [source], "distance": 0.0, "explored": [source], "explored_edges": []}

    # Distance from source to each node
    dist = {source: 0.0}
    # Previous node in shortest path
    prev = {source: None}
    # Min-heap: (distance, node)
    heap = [(0.0, source)]
    # Track exploration order for visualization
    explored_order = []
    explored_edges = []
    visited = set()

    while heap:
        # Step 1: Pop the node with the smallest known distance
        current_dist, current = heapq.heappop(heap)

        # Skip if we already found a shorter path to this node
        if current in visited:
            continue
        visited.add(current)
        explored_order.append(current)

        # Step 2: Early exit if we reached the target
        if current == target:
            break

        # Step 3: Explore all neighbors of the current node
        for neighbor, weight in graph.get(current, []):
            if neighbor in visited:
                continue
            
            # Calculate distance to neighbor through the current node
            new_dist = current_dist + weight
            
            # If this path is shorter than any previously known path, update it
            if new_dist < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_dist
                prev[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))
                explored_edges.append((current, neighbor))

    # Reconstruct path
    path = []
    node = target
    if target in prev or target == source:
        while node is not None:
            path.append(node)
            node = prev.get(node)
        path.reverse()

    return {
        "path": path,
        "distance": dist.get(target, float("inf")),
        "explored": explored_order,
        "explored_edges": explored_edges,
    }


def multi_stop_dijkstra(
    graph: dict[tuple[int, int], list[tuple[tuple[int, int], float]]],
    source: tuple[int, int],
    stops: list[tuple[int, int]],
) -> dict:
    """
    Compute shortest path visiting all stops in the given order.
    Chains Dijkstra calls between consecutive waypoints.

    Args:
        graph: Adjacency list
        source: Starting position
        stops: Ordered list of locations to visit

    Returns:
        {
            "path": [...],        # Full path through all stops
            "distance": float,    # Total travel distance
            "segments": [...]     # Per-segment results
        }
    """
    full_path = [source]
    total_distance = 0.0
    segments = []
    current = source

    for stop in stops:
        result = dijkstra(graph, current, stop)
        if result["distance"] == float("inf"):
            # No path found to this stop
            segments.append({
                "from": current, "to": stop,
                "distance": float("inf"), "reachable": False
            })
            continue

        # Append path (skip first node to avoid duplicates)
        if result["path"]:
            full_path.extend(result["path"][1:])
        total_distance += result["distance"]
        segments.append({
            "from": current, "to": stop,
            "distance": result["distance"], "reachable": True
        })
        current = stop

    return {
        "path": full_path,
        "distance": total_distance,
        "segments": segments,
    }


def _greedy_route(
    graph: dict[tuple[int, int], list[tuple[tuple[int, int], float]]],
    source: tuple[int, int],
    stops: list[tuple[int, int]],
) -> dict:
    """
    Greedy nearest-neighbor routing: always go to the closest unvisited stop.
    Used as a comparison baseline against optimal routing.
    """
    remaining = list(stops)
    order = []
    current = source
    total_distance = 0.0
    full_path = [source]

    while remaining:
        # Find nearest unvisited stop
        best_stop = None
        best_dist = float("inf")
        best_result = None

        for stop in remaining:
            result = dijkstra(graph, current, stop)
            if result["distance"] < best_dist:
                best_dist = result["distance"]
                best_stop = stop
                best_result = result

        if best_stop is None or best_dist == float("inf"):
            break

        remaining.remove(best_stop)
        order.append(best_stop)
        total_distance += best_dist
        if best_result["path"]:
            full_path.extend(best_result["path"][1:])
        current = best_stop

    return {
        "path": full_path,
        "distance": total_distance,
        "visit_order": order,
    }


def _naive_route(
    graph: dict[tuple[int, int], list[tuple[tuple[int, int], float]]],
    source: tuple[int, int],
    stops: list[tuple[int, int]],
) -> dict:
    """
    Naive routing: visit stops in the order they appear (no optimization).
    """
    return multi_stop_dijkstra(graph, source, stops)


def compare_routing(
    graph: dict[tuple[int, int], list[tuple[tuple[int, int], float]]],
    source: tuple[int, int],
    stops: list[tuple[int, int]],
) -> dict:
    """
    Compare three routing strategies:
    1. Dijkstra (optimal via Held-Karp or ordered)
    2. Greedy nearest-neighbor
    3. Naive (original order)

    Returns comparison metrics for all three approaches.
    """
    naive = _naive_route(graph, source, stops)
    greedy = _greedy_route(graph, source, stops)

    return {
        "naive": {
            "path": naive["path"],
            "distance": naive["distance"],
            "visit_order": stops,
            "label": "Naive (Original Order)",
        },
        "greedy": {
            "path": greedy["path"],
            "distance": greedy["distance"],
            "visit_order": greedy["visit_order"],
            "label": "Greedy (Nearest Neighbor)",
        },
    }


def compute_distance_matrix(
    graph: dict[tuple[int, int], list[tuple[tuple[int, int], float]]],
    locations: list[tuple[int, int]],
) -> list[list[float]]:
    """
    Precompute pairwise shortest distances between all given locations.
    Used as input for Held-Karp TSP and other optimizations.

    Returns:
        n×n distance matrix where matrix[i][j] = shortest distance from locations[i] to locations[j]
    """
    n = len(locations)
    matrix = []
    for _ in range(n):
        row = []
        for _ in range(n):
            row.append(float("inf"))
        matrix.append(row)

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 0.0
            else:
                result = dijkstra(graph, locations[i], locations[j])
                matrix[i][j] = result["distance"]

    return matrix
