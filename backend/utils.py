import math
from typing import Any

def sanitize_json(obj: Any) -> Any:
    """Recursively replace inf/nan floats with None so JSON serialization never fails."""
    if isinstance(obj, float):
        return None if (math.isinf(obj) or math.isnan(obj)) else obj
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_json(v) for v in obj]
    return obj
