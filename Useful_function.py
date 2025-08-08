from typing import Any, List, Type


def calculate_type_density(
    grid: List[List[Any]],
    x: int,
    y: int,
    direction: str,
    scan_range: int,
    entity_type: Type,
) -> float:
    """
    Calculate the density of a specific entity type in a given direction.

    Args:
        grid: The game grid
        x: Current x position
        y: Current y position
        direction: Direction to scan ("NE", "NW", "SE", "SW")
        scan_range: Range to scan
        entity_type: Type of entity to count (Food, Blob, etc.)

    Returns:
        Density value (float)
    """
    count = 0
    total_cells = 0

    if direction == "NE":
        for i in range(1, scan_range + 1):
            for j in range(1, scan_range + 1):
                if x + i < len(grid) and y - j >= 0:
                    if isinstance(grid[x + i][y - j], entity_type):
                        count += 1
                    total_cells += 1
    elif direction == "NW":
        for i in range(1, scan_range + 1):
            for j in range(1, scan_range + 1):
                if x - i >= 0 and y - j >= 0:
                    if isinstance(grid[x - i][y - j], entity_type):
                        count += 1
                    total_cells += 1
    elif direction == "SE":
        for i in range(1, scan_range + 1):
            for j in range(1, scan_range + 1):
                if x + i < len(grid) and y + j < len(grid[0]):
                    if isinstance(grid[x + i][y + j], entity_type):
                        count += 1
                    total_cells += 1
    elif direction == "SW":
        for i in range(1, scan_range + 1):
            for j in range(1, scan_range + 1):
                if x - i >= 0 and y + j < len(grid[0]):
                    if isinstance(grid[x - i][y + j], entity_type):
                        count += 1
                    total_cells += 1

    return count / max(total_cells, 1)  # Avoid division by zero
