import math
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Optional
from utils import sanitize_json

router = APIRouter(prefix="/api/algorithms", tags=["algorithms"])


class DijkstraRequest(BaseModel):
    source: list[int]  # [row, col]
    target: list[int]  # [row, col]


class BinPackingRequest(BaseModel):
    num_products: Optional[int] = None
    rerun: bool = True


class HeldKarpRequest(BaseModel):
    locations: list[list[int]] = []  # [[row,col], ...]
    start: list[int] = [28, 2]
    num_random: Optional[int] = None


class GreedyRequest(BaseModel):
    order_id: Optional[int] = None
    custom_location: Optional[list[int]] = None


@router.post("/dijkstra")
async def run_dijkstra(req: DijkstraRequest):
    """Run Dijkstra's algorithm between two points with visualization data."""
    from main import simulation_engine
    from algorithms.dijkstra import dijkstra
    
    # Snap coordinates to nearest walkable path
    source = simulation_engine.graph.get_location_for_cell(req.source[0], req.source[1]) or tuple(req.source)
    target = simulation_engine.graph.get_location_for_cell(req.target[0], req.target[1]) or tuple(req.target)
    
    graph = simulation_engine.graph.adjacency
    result = dijkstra(graph, source, target)
    result["path"] = [list(p) for p in result["path"]]
    result["explored"] = [list(e) for e in result["explored"]]
    result["explored_edges"] = [[list(e[0]), list(e[1])] for e in result["explored_edges"]]
    return sanitize_json({"result": result, "algorithm": "Dijkstra's Shortest Path"})


@router.post("/dijkstra/compare")
async def compare_dijkstra(req: HeldKarpRequest):
    """Compare Dijkstra vs Greedy vs Naive routing."""
    from main import simulation_engine
    from algorithms.dijkstra import compare_routing
    graph = simulation_engine.graph.adjacency
    source = tuple(req.start)
    stops = [tuple(loc) for loc in req.locations]

    if not stops:
        # Use random shelf locations
        import random
        shelf_points = list(simulation_engine.graph.shelf_access_points.values())
        stops = random.sample(shelf_points, min(6, len(shelf_points)))

    result = compare_routing(graph, source, stops)
    # Serialize tuples
    for key in ["naive", "greedy"]:
        if key in result:
            result[key]["path"] = [list(p) for p in result[key]["path"]]
            result[key]["visit_order"] = [list(v) for v in result[key]["visit_order"]]
    return sanitize_json({"result": result})


@router.post("/bin-packing")
async def run_bin_packing(req: BinPackingRequest):
    """Run slotting optimization and return results."""
    from main import simulation_engine
    from algorithms.bin_packing import optimize_slotting
    from models.warehouse import CellType

    products = list(simulation_engine.products.values())
    if req.num_products:
        import random
        products = random.sample(products, min(req.num_products, len(products)))

    shelves = []
    if simulation_engine.layout:
        for r in range(simulation_engine.layout.rows):
            for c in range(simulation_engine.layout.cols):
                cell = simulation_engine.layout.grid[r][c]
                if cell["cell_type"] == CellType.SHELF.value and cell.get("shelf_id") is not None:
                    shelves.append({
                        "id": cell["shelf_id"], "capacity": cell["shelf_capacity"],
                        "row": r, "col": c, "zone": cell.get("zone", "C"),
                    })

    result = optimize_slotting(products, shelves)
    return sanitize_json({"result": result, "algorithm": "First Fit Decreasing + ABC Classification"})


@router.post("/held-karp")
async def run_held_karp(req: HeldKarpRequest):
    """Run Held-Karp TSP optimization on pick locations."""
    from main import simulation_engine
    from algorithms.dijkstra import compute_distance_matrix
    from algorithms.held_karp import compare_pick_routes
    import random

    locations = [tuple(loc) for loc in req.locations]
    if not locations:
        shelf_points = list(simulation_engine.graph.shelf_access_points.values())
        count = req.num_random if req.num_random else 8
        locations = random.sample(shelf_points, min(count, len(shelf_points)))

    # Snap start position to nearest walkable path
    start_pos = simulation_engine.graph.get_location_for_cell(req.start[0], req.start[1]) or tuple(req.start)
    all_locs = [start_pos] + locations
    labels = ["Start"] + [f"Pick {i+1}" for i in range(len(locations))]

    dist_matrix = compute_distance_matrix(simulation_engine.graph.adjacency, all_locs)
    result = compare_pick_routes(dist_matrix, labels, start=0, return_to_start=True)

    # Add actual coordinates
    result["coordinates"] = [list(loc) for loc in all_locs]
    return sanitize_json({"result": result, "algorithm": "Held-Karp DP vs Greedy NN"})


@router.post("/greedy-assignment")
async def run_greedy_assignment(req: GreedyRequest):
    """Demo greedy order assignment."""
    from main import simulation_engine
    from algorithms.greedy_assignment import assign_order_greedy, calculate_picker_metrics

    if req.custom_location:
        order = {
            "id": -2, "custom": True, "location": req.custom_location,
            "items": [{"product_name": "Dynamic Request", "shelf_location": req.custom_location}]
        }
    elif req.order_id and req.order_id in simulation_engine.orders:
        order = simulation_engine.orders[req.order_id]
    else:
        # Create a demo order
        import random
        products = list(simulation_engine.products.values())
        sample = random.sample(products, min(3, len(products)))
        order = {
            "id": -1, "items": [
                {"product_id": p["id"], "product_name": p["name"], "quantity": 1, "shelf_location": p.get("shelf_location")}
                for p in sample if p.get("shelf_location")
            ]
        }

    def dist_func(a, b):
        return simulation_engine.graph.distance(tuple(a), tuple(b))

    picker_list = list(simulation_engine.pickers.values())
    assignment = assign_order_greedy(order, picker_list, dist_func, ignore_busy=True)
    
    # Add full picker object to assignment for frontend
    if assignment["assigned_picker_id"] is not None:
        assignment["picker"] = simulation_engine.pickers[assignment["assigned_picker_id"]]
        
    metrics = calculate_picker_metrics(picker_list, simulation_engine.completed_orders)

    return sanitize_json({
        "assignment": {**assignment, "order": order}, 
        "metrics": metrics, 
        "algorithm": "Greedy Nearest Picker"
    })


@router.get("/compare")
async def compare_all():
    """Get comparison metrics across all algorithms."""
    from main import simulation_engine
    from algorithms.greedy_assignment import calculate_picker_metrics

    metrics = calculate_picker_metrics(list(simulation_engine.pickers.values()), simulation_engine.completed_orders)
    sim_metrics = simulation_engine._compute_metrics()

    return sanitize_json({
        "picker_metrics": metrics,
        "simulation_metrics": sim_metrics,
        "algorithms_used": [
            {"name": "Dijkstra's Algorithm", "purpose": "Shortest path between locations", "complexity": "O((V+E) log V)"},
            {"name": "First Fit Decreasing", "purpose": "Bin packing for shelf allocation", "complexity": "O(n × m)"},
            {"name": "Held-Karp DP", "purpose": "Optimal pick route (TSP)", "complexity": "O(n² × 2ⁿ)"},
            {"name": "Greedy Assignment", "purpose": "Real-time order-to-picker assignment", "complexity": "O(P) per order"},
        ],
    })
