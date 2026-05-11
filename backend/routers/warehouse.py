"""
Smart Warehouse System — Warehouse API Routes
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/warehouse", tags=["warehouse"])


@router.get("/layout")
async def get_layout():
    """Get current warehouse grid layout and graph data."""
    from main import simulation_engine
    state = simulation_engine.get_state()
    layout = state.get("layout")
    graph_data = simulation_engine.graph.to_serializable()
    return {"layout": layout, "graph": graph_data}


@router.get("/shelves")
async def get_shelves():
    """Get all shelf details with capacity and contents."""
    from main import simulation_engine
    shelves = []
    if simulation_engine.layout:
        for r in range(simulation_engine.layout.rows):
            for c in range(simulation_engine.layout.cols):
                cell = simulation_engine.layout.grid[r][c]
                if cell["cell_type"] == "shelf":
                    shelves.append({
                        "shelf_id": cell.get("shelf_id"),
                        "row": r, "col": c,
                        "zone": cell.get("zone"),
                        "capacity": cell.get("shelf_capacity", 0),
                        "used": cell.get("shelf_used", 0),
                        "utilization": round(cell["shelf_used"] / cell["shelf_capacity"] * 100, 1) if cell["shelf_capacity"] > 0 else 0,
                        "products": cell.get("products", []),
                    })
    return {"shelves": shelves, "total": len(shelves)}
