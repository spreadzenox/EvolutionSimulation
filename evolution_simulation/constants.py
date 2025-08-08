from typing import Dict, Tuple

# Simulation parameters
FRAMERATE: int = 30
HIT_RANGE: int = 1
EAT_RANGE: int = 3
REPRODUCE_RATE: int = 100
ENERGY_DECAY_PER_TURN: int = 1
ATTACK_COST: int = 1
ATTACK_KIN_PENALTY: int = 10
BASE_ENERGY: int = 30
REPRODUCE_DISTANCE: int = 3
MOOVE_SPEED: int = 1
SCAN_RANGE: int = 7
DENSITY_SCAN_RANGE: int = 10
MUTATION_RATE: float = 0.1
MUTATION_POWER: float = 0.5
FOOD_RATE: float = 0.95
RESET_FOOD_RATE: float = 0.002
BLOB_RATE: float = 1 - FOOD_RATE
SPAWN_RATE: float = 0.2
RESET_SPAWN_RATE: float = 0.001
TAILLE_GRID: int = 400

# Decision & exploration tuning
ACTION_PENALTY_DECAY: float = 0.9
ACTION_FAIL_PENALTY_INCREMENT: float = 0.4
ACTION_PENALTY_MAX: float = 1.5
SOFTMAX_TEMPERATURE_MIN: float = 0.4
SOFTMAX_TEMPERATURE_MAX: float = 1.2
HIT_COOLDOWN_TURNS: int = 3
LOOP_PENALTY_INCREMENT: float = 0.2
LOOP_REPEAT_THRESHOLD: int = 6

# Display parameters (main window must be square)
WIDTH: int = 900
HEIGHT: int = 900
WIDTH_INFO: int = 600

COLOR: Dict[str, Tuple[int, int, int]] = {
    "WHITE": (255, 255, 255),
    "YELLOW": (255, 255, 0),
    "BLUE": (100, 149, 237),
    "RED": (188, 39, 50),
    "DARK_GREY": (80, 78, 81),
    "GREEN": (0, 255, 0),
    "ORANGE": (255, 165, 0),
    "PURPLE": (128, 0, 128),
    "CYAN": (0, 255, 255),
    "LIGHT_GREY": (200, 200, 200),
    "DARK_BLUE": (50, 50, 150),
    "BLACK": (0, 0, 0),
}
