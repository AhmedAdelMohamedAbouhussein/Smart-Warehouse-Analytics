# Smart Warehouse: Line-by-Line Algorithmic Explanation

This document provides a deep-dive into the four core algorithms powering the Smart Warehouse System. Each section explains the logic, complexity, and specific implementation details found in the source code.

---

**Complexity Summary:**
1. **Dijkstra**: $O(E \log V)$
2. **Held-Karp**: $O(n^2 2^n)$
3. **Bin Packing**: $O(n \log n + n \cdot m)$
4. **Greedy Assignment**: $O(P)$

## Source Code Reference

### 1. Dijkstra Implementation
```python
def dijkstra(graph, source, target):
    dist = {source: 0.0}
    prev = {source: None}
    heap = [(0.0, source)]
    visited = set()

    while heap:
        current_dist, current = heapq.heappop(heap)
        if current in visited: continue
        visited.add(current)
        if current == target: break

        for neighbor, weight in graph.get(current, []):
            if neighbor in visited: continue
            new_dist = current_dist + weight
            if new_dist < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_dist
                prev[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))
    
    # Path Reconstruction
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = prev.get(node)
    return path[::-1]
```

### 2. Held-Karp (TSP) Implementation
```python
def held_karp_tsp(distance_matrix, start=0):
    n = len(distance_matrix)
    dp = {}
    parent = {}
    
    # Base Case
    for i in range(n):
        if i == start: continue
        dp[(1 << start | 1 << i, i)] = distance_matrix[start][i]
        parent[(1 << start | 1 << i, i)] = start

    # DP Subsets
    for size in range(3, n + 1):
        for subset in itertools.combinations(range(n), size):
            if start not in subset: continue
            mask = sum(1 << i for i in subset)
            for end in subset:
                if end == start: continue
                prev_mask = mask & ~(1 << end)
                best_cost = min((dp.get((prev_mask, p), float('inf')) + distance_matrix[p][end], p) 
                                for p in subset if p != end and p != start)
                dp[(mask, end)], parent[(mask, end)] = best_cost
```

### 3. Bin Packing (FFD) Implementation
```python
def first_fit_decreasing(items, bins):
    # Sort items by volume descending (FFD strategy)
    sorted_items = sorted(items, key=lambda x: x.get("volume", 0), reverse=True)
    bin_remaining = {b["id"]: b.get("capacity", 100) for b in bins}
    placements = {}

    for item in sorted_items:
        for b in bins:
            if bin_remaining[b["id"]] >= item["volume"]:
                placements[item["id"]] = b["id"]
                bin_remaining[b["id"]] -= item["volume"]
                break
    return placements
```

### 4. Greedy Order Assignment Implementation
```python
def assign_order_greedy(order, pickers, distance_func):
    first_item_loc = order["items"][0]["shelf_location"]
    best_picker = None
    min_dist = float("inf")

    for picker in pickers:
        if picker["status"] == "idle":
            d = distance_func(picker["current_position"], first_item_loc)
            if d < min_dist:
                min_dist = d
                best_picker = picker["id"]
    return best_picker
```


---

## 1. Dijkstra’s Algorithm (Shortest Path)
**File**: `backend/algorithms/dijkstra.py`

### Line-by-Line Breakdown:
*   **L14**: `def dijkstra(graph, source, target):` -> Defines the core pathfinding function using an adjacency list graph.
*   **L35**: `if source not in graph:` -> Safety check: if the starting point doesn't exist in the map, exit.
*   **L41**: `dist = {source: 0.0}` -> Initializes the source node with a distance of zero.
*   **L43**: `prev = {source: None}` -> Creates a dictionary to store the "parent" of each node for path reconstruction.
*   **L45**: `heap = [(0.0, source)]` -> Sets up the min-priority queue (Min-Heap) to always process the closest node first.
*   **L49**: `visited = set()` -> Tracks nodes that have already been finalized to avoid redundant processing.
*   **L51**: `while heap:` -> Continues the search as long as there are reachable nodes to explore.
*   **L52**: `current_dist, current = heapq.heappop(heap)` -> Extracts the node with the smallest known distance from the heap.
*   **L54**: `if current in visited: continue` -> Skips the node if we have already found a shorter path to it.
*   **L56**: `visited.add(current)` -> Marks the current node as finalized.
*   **L60**: `if current == target: break` -> **Optimization**: Stops the algorithm early once the destination is reached.
*   **L64**: `for neighbor, weight in graph.get(current, []):` -> Examines every node adjacent to the current one.
*   **L67**: `new_dist = current_dist + weight` -> Calculates the distance to the neighbor through the current path.
*   **L68**: `if new_dist < dist.get(neighbor, float("inf")):` -> **Relaxation**: Checks if this new path is shorter than the best one found so far.
*   **L69**: `dist[neighbor] = new_dist` -> Updates the neighbor with the new, shorter distance.
*   **L70**: `prev[neighbor] = current` -> Records that the best way to reach this neighbor is through the current node.
*   **L71**: `heapq.heappush(heap, (new_dist, neighbor))` -> Adds the neighbor to the heap to explore its own neighbors later.
*   **L78**: `while node is not None:` -> Backtracks from the target using the `prev` dictionary to rebuild the path.
*   **L81**: `path.reverse()` -> Flips the reconstructed list so it goes from source to target.

---

## 2. Held-Karp Algorithm (TSP Optimization)
**File**: `backend/algorithms/held_karp.py`

### Line-by-Line Breakdown:
*   **L11**: `def held_karp_tsp(distance_matrix, ...):` -> Entrance to the exact TSP solver using Dynamic Programming.
*   **L24**: `dp = {}` -> The DP table where we store `(visited_mask, last_node): min_cost`.
*   **L27**: `start_mask = 1 << start` -> Uses a bitmask to represent the set of visited nodes (e.g., `1` is node 0).
*   **L30**: `for i in range(n):` -> Loops through all nodes to establish the base cases.
*   **L33**: `mask = start_mask | (1 << i)` -> Creates a mask representing the subset `{start, i}`.
*   **L34**: `dp[(mask, i)] = distance_matrix[start][i]` -> Sets the initial cost to go from start directly to node `i`.
*   **L38**: `for subset_size in range(3, n + 1):` -> Iteratively builds paths for larger and larger subsets of locations.
*   **L40**: `for subset in itertools.combinations(other_nodes, subset_size - 1):` -> Generates every possible subset of nodes to check.
*   **L43**: `mask |= (1 << node)` -> Converts the current subset into a unique bitmask key.
*   **L45**: `prev_mask = mask & ~(1 << end)` -> Identifies the subset that existed before visiting the `end` node.
*   **L51**: `prev_cost = dp.get((prev_mask, prev), float("inf"))` -> Retrieves the pre-calculated optimal cost for the previous subset.
*   **L54**: `total = prev_cost + distance_matrix[prev][end]` -> **The Recurrence**: Adds the travel cost to the current node.
*   **L56**: `if total < best_cost:` -> Finds the absolute minimum cost to reach the current subset configuration.
*   **L72**: `cost += distance_matrix[last][start]` -> Completes the loop by adding the return trip to the warehouse station.
*   **L89**: `mask = mask & ~(1 << current)` -> Uses bitwise `NOT` and `AND` to backtrack through the optimal path.

---

## 3. Bin Packing (Slotting Optimization)
**File**: `backend/algorithms/bin_packing.py`

### Line-by-Line Breakdown:
*   **L44**: `sorted_products = sorted(products, ..., reverse=True)` -> Sorts items by demand frequency to prioritize high-velocity stock.
*   **L68**: `cumulative += freq` -> Tracks the running total of demand to calculate the "Velocity Class."
*   **L71**: `if cum_pct <= config.ABC_A_THRESHOLD:` -> Categorizes the top tier of products as "Zone A" (High Priority).
*   **L116**: `sorted_items = sorted(items, ..., reverse=True)` -> Sorts items by volume (FFD strategy) to fit large items first.
*   **L119**: `bin_remaining = {b["id"]: b.get("capacity")}` -> Initializes a tracker for the available cubic space in every shelf.
*   **L132**: `for b in bins:` -> The "First Fit" loop: looks at every bin in sequence.
*   **L134**: `if bin_remaining[bin_id] >= item_volume:` -> Logic check: does this item fit in the current shelf?
*   **L136**: `placements[item_id] = bin_id` -> Officially assigns the product to the physical shelf ID.
*   **L137**: `bin_remaining[bin_id] -= item_volume` -> Subtracts the item's volume from the shelf's remaining capacity.
*   **L245**: `result = first_fit_decreasing(items, zone_bins)` -> Executes the packing algorithm within a specific warehouse zone (A, B, or C).

---

## 4. Greedy Real-Time Assignment
**File**: `backend/algorithms/greedy_assignment.py`

### Line-by-Line Breakdown:
*   **L16**: `pick_locations = []` -> Extracts all item locations from the newly received order.
*   **L25**: `first_location = pick_locations[0]` -> Targets the first item in the order as the "Cost Anchor."
*   **L32**: `for picker in pickers:` -> Iterates through every robot in the warehouse fleet.
*   **L35**: `is_available = status == "idle"` -> Safety check: only considers robots that aren't already busy.
*   **L39**: `dist = distance_func(pos, first_location)` -> Calculates the path distance from robot to order.
*   **L49**: `if is_available and dist < best_distance:` -> **The Greedy Choice**: Selects the absolute closest robot.
*   **L51**: `best_picker_id = picker["id"]` -> Locks in the assignment for the winning robot.
*   **L83**: `utilization = (active_t / total_t * 100)` -> Calculates how hard each robot is working (Active vs. Idle).

---
