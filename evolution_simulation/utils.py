from typing import Any, List, Type


def calculate_type_density(
    grid: List[List[Any]],
    x: int,
    y: int,
    direction: str,
    scan_range: int,
    entity_type: Type,
) -> float:
    """Calculate the density of a specific entity type in a given direction.

    Optimized to avoid repeated bound checks and expensive operations.
    """
    count = 0
    total_cells = 0

    if direction == "NE":
        x_range = range(x + 1, min(x + scan_range + 1, len(grid)))
        y_range = range(max(y - scan_range, 0), y)
    elif direction == "NW":
        x_range = range(max(x - scan_range, 0), x)
        y_range = range(max(y - scan_range, 0), y)
    elif direction == "SE":
        x_range = range(x + 1, min(x + scan_range + 1, len(grid)))
        y_range = range(y + 1, min(y + scan_range + 1, len(grid[0])))
    elif direction == "SW":
        x_range = range(max(x - scan_range, 0), x)
        y_range = range(y + 1, min(y + scan_range + 1, len(grid[0])))
    else:
        return 0.0

    for i in x_range:
        for j in y_range:
            if grid[i][j]:
                if isinstance(grid[i][j][0], entity_type):
                    count += 1
            total_cells += 1

    return count / max(total_cells, 1)
