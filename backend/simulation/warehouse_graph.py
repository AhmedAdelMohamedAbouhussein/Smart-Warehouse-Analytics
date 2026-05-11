"""
Smart Warehouse System — Warehouse Graph Builder
Converts the warehouse grid layout into a weighted directed graph for pathfinding.
"""
from __future__ import annotations
from models.warehouse import WarehouseLayout, CellType
import config


class WarehouseGraph:
    """
    Weighted directed graph representation of the warehouse floor.
    Nodes = walkable cells (paths, stations, receiving docks).
    Edges = connections between adjacent walkable cells.
    Weights = travel distance/time.
    """

    def __init__(self):
        self.adjacency: dict[tuple[int, int], list[tuple[tuple[int, int], float]]] = {}
        self.nodes: set[tuple[int, int]] = set()
        self.shelf_access_points: dict[int, tuple[int, int]] = {}  # shelf_id -> nearest path
        self._shelf_positions: dict[int, tuple[int, int]] = {}

    def build_from_layout(self, layout: WarehouseLayout):
        """
        Build graph from warehouse grid layout.
        Creates nodes for all walkable cells and edges to adjacent walkable cells.
        Also maps each shelf to its nearest walkable access point.
        """
        self.adjacency.clear()
        self.nodes.clear()
        self.shelf_access_points.clear()
        self._shelf_positions.clear()

        grid = layout.grid
        rows = layout.rows
        cols = layout.cols

        walkable_types = {CellType.PATH.value, CellType.PICK_STATION.value, CellType.RECEIVING.value}

        # Step 1: Identify all walkable nodes
        for r in range(rows):
            for c in range(cols):
                cell = grid[r][c]
                if cell["cell_type"] in walkable_types:
                    self.nodes.add((r, c))
                    self.adjacency[(r, c)] = []
                elif cell["cell_type"] == CellType.SHELF.value and cell.get("shelf_id") is not None:
                    self._shelf_positions[cell["shelf_id"]] = (r, c)

        # Step 2: Create edges between adjacent walkable cells (4-directional)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        for (r, c) in self.nodes:
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if (nr, nc) in self.nodes:
                    weight = config.EDGE_WEIGHT_STRAIGHT
                    self.adjacency[(r, c)].append(((nr, nc), weight))

        # Step 3: Map shelves to nearest walkable access points
        for shelf_id, (sr, sc) in self._shelf_positions.items():
            best_access = None
            best_dist = float("inf")
            for dr, dc in directions:
                nr, nc = sr + dr, sc + dc
                if (nr, nc) in self.nodes:
                    dist = config.EDGE_WEIGHT_STRAIGHT
                    if best_access is None or dist < best_dist:
                        best_access = (nr, nc)
                        best_dist = dist
            if best_access:
                self.shelf_access_points[shelf_id] = best_access

    def get_shelf_access_point(self, shelf_id: int) -> tuple[int, int] | None:
        """Get the walkable cell adjacent to a shelf (for picker to stand at)."""
        return self.shelf_access_points.get(shelf_id)

    def get_location_for_cell(self, row: int, col: int) -> tuple[int, int] | None:
        """Get the nearest walkable node for any cell (including shelves)."""
        if (row, col) in self.nodes:
            return (row, col)
        # Find nearest walkable neighbor
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if (nr, nc) in self.nodes:
                return (nr, nc)
        return None

    def get_pick_stations(self, layout: WarehouseLayout) -> list[tuple[int, int]]:
        """Get all pick station positions."""
        stations = []
        for r in range(layout.rows):
            for c in range(layout.cols):
                if layout.grid[r][c]["cell_type"] == CellType.PICK_STATION.value:
                    stations.append((r, c))
        return stations

    def get_receiving_docks(self, layout: WarehouseLayout) -> list[tuple[int, int]]:
        """Get all receiving dock positions."""
        docks = []
        for r in range(layout.rows):
            for c in range(layout.cols):
                if layout.grid[r][c]["cell_type"] == CellType.RECEIVING.value:
                    docks.append((r, c))
        return docks

    def distance(self, a: tuple[int, int], b: tuple[int, int]) -> float:
        """Quick shortest distance between two nodes using Dijkstra."""
        from algorithms.dijkstra import dijkstra
        result = dijkstra(self.adjacency, a, b)
        return result["distance"]

    def to_serializable(self) -> dict:
        """Convert graph to JSON-serializable format."""
        edges = []
        for node, neighbors in self.adjacency.items():
            for neighbor, weight in neighbors:
                edges.append({"from": list(node), "to": list(neighbor), "weight": weight})
        return {
            "nodes": [list(n) for n in self.nodes],
            "edges": edges,
            "node_count": len(self.nodes),
            "edge_count": len(edges),
            "shelf_access_points": {str(k): list(v) for k, v in self.shelf_access_points.items()},
        }
