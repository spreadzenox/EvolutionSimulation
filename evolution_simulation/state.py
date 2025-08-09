from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame

from . import constants as C

if TYPE_CHECKING:
    from .entities import Grid
    from .ui import ImageManager


@dataclass
class AppState:
    # Dynamic simulation state
    grid: Grid | None = None
    turn: int = 0
    running: bool = True
    sim_running: bool = True
    game_state: str = "menu"  # "menu" | "simulation"

    # Dynamic parameters (can be changed via sliders)
    TAILLE_GRID: int = C.TAILLE_GRID
    MAX_SPAWN_ENERGY: int = C.MAX_SPAWN_ENERGY
    MUTATION_RATE: float = C.MUTATION_RATE
    FOOD_RATE: float = C.FOOD_RATE
    RESET_FOOD_RATE: float = C.RESET_FOOD_RATE
    SPAWN_RATE: float = C.SPAWN_RATE
    RESET_SPAWN_RATE: float = C.RESET_SPAWN_RATE
    SCAN_RANGE: int = C.SCAN_RANGE

    # View
    CELL_SIZE: float = field(init=False)
    SCALE_X: float = 1.0
    SCALE_Y: float = 1.0
    WIN: pygame.Surface | None = None
    FONT: pygame.font.Font | None = None
    FONT_PETIT: pygame.font.Font | None = None
    FONT_GRAND: pygame.font.Font | None = None

    # FPS
    current_fps: float = 30.0
    target_fps: int = 30

    # Assets
    image_manager: ImageManager | None = None

    def __post_init__(self) -> None:
        self.CELL_SIZE = C.HEIGHT / max(self.TAILLE_GRID, 1)


state = AppState()
