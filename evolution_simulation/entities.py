from __future__ import annotations

import random as rd
from collections import deque
from typing import Any, cast

import numpy as np
import pygame

from . import constants as C
from .state import state
from .utils import calculate_type_density


def distance(obj1: Any, obj2: Any) -> int:
    return int(abs(obj1.x - obj2.x) + abs(obj1.y - obj2.y))


def dist_x(source: Any, destination: Any) -> int:
    dx = destination.x - source.x
    # No wrapping: direct difference only
    return int(dx)


def dist_y(source: Any, destination: Any) -> int:
    dy = destination.y - source.y
    # No wrapping: direct difference only
    return int(dy)


class Brain:
    def __init__(
        self, blob: Any, input_size: int = 17, output_size: int = 7, n_layer: int = 4
    ) -> None:
        self.blob = blob
        self.weight = [
            np.random.randn(input_size, 20),
            np.random.randn(20, 15),
            np.random.randn(15, 10),
            np.random.randn(10, output_size),
        ]

    def predict(self, entree: np.ndarray) -> np.ndarray:
        x = entree
        for w in self.weight:
            x = np.tanh(np.dot(x, w))
        return x


class Food:
    def __init__(self, x: int, y: int, amount: int) -> None:
        self.x = x
        self.y = y
        self.amount = amount
        self.color = C.COLOR["YELLOW"]

    def draw(self, win: pygame.Surface) -> None:
        x = self.x * state.CELL_SIZE
        y = self.y * state.CELL_SIZE
        if state.image_manager and state.image_manager.food_image:
            win.blit(state.image_manager.food_image, (x, y))
        else:
            center_x = x + state.CELL_SIZE / 2
            center_y = y + state.CELL_SIZE / 2
            pygame.draw.circle(
                win, self.color, (center_x, center_y), state.CELL_SIZE / 4
            )

    def update(self) -> None:
        pass

    def suicide(self) -> None:
        if state.grid is not None:
            if self in state.grid.grid[self.x][self.y]:
                state.grid.grid[self.x][self.y].remove(self)


class BlobImage:
    def __init__(
        self, x: float, y: float, radius: float, color: tuple[int, int, int], blob: Any
    ) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.blob = blob


class Blob:
    TIMESTEP: float = 0.1
    NEXT_ID: int = 1

    def __init__(
        self,
        x: int,
        y: int,
        energy: int,
        grid: Grid,
        brain: Any = 0,
        mutation_rate: float = 0,
        parent_ids: tuple[int, int] | None = None,
    ) -> None:
        self.id = Blob.NEXT_ID
        Blob.NEXT_ID += 1
        self.parent_ids: tuple[int, int] | tuple[()] = parent_ids or ()
        self.birth_turn = state.turn
        self.x = x
        self.y = y
        self.grid = grid
        x_real = self.x * state.CELL_SIZE + state.CELL_SIZE / 2
        y_real = self.y * state.CELL_SIZE + state.CELL_SIZE / 2
        self.radius = state.CELL_SIZE / 2
        self.color = (0, min([energy * 5, 255]), max([0, 255 - energy * 5]))
        self.energy = energy
        self.behaviour: list[str] = []
        self.fail = 0
        self.image = BlobImage(
            color=self.color, x=x_real, y=y_real, radius=self.radius, blob=self
        )
        self.mutation_rate = mutation_rate or C.MUTATION_RATE
        self.brain = brain if brain != 0 else Brain(blob=self)
        if brain != 0:
            self.brain.blob = self
        self.grid.list_blobs.append(self)
        self.scan_cache: dict[str, Any] = {}
        self.last_scan_turn = -1
        self.cache_size_limit = 10
        self.recent_actions: deque[int] = deque(maxlen=C.LOOP_REPEAT_THRESHOLD)
        self.last_hit_turn: int = -C.HIT_COOLDOWN_TURNS
        # One penalty per action: 0=eat, 1-4=move, 5=hit, 6=reproduce
        self.action_penalties: list[float] = [0.0] * 7

    def update(self) -> None:
        self.color = (0, min([self.energy * 5, 255]), max([0, 255 - self.energy * 5]))
        self.radius = state.CELL_SIZE / 2
        x_real = self.x * state.CELL_SIZE + state.CELL_SIZE / 2
        y_real = self.y * state.CELL_SIZE + state.CELL_SIZE / 2
        self.image.color = self.color
        self.image.x = x_real
        self.image.y = y_real
        self.image.radius = self.radius

    def draw(self, win: pygame.Surface) -> None:
        x = self.x * state.CELL_SIZE
        y = self.y * state.CELL_SIZE
        if self.energy > 0:
            is_best = False
            if state.grid is not None and state.grid.better_blob is self:
                is_best = True

            center_x = x + state.CELL_SIZE / 2
            center_y = y + state.CELL_SIZE / 2

            if state.image_manager and state.image_manager.blob_image:
                if is_best:
                    # Render highlighted: yellow fill and red outline
                    colored_image = state.image_manager.blob_image.copy()
                    colored_image.fill(
                        C.COLOR["YELLOW"], special_flags=pygame.BLEND_MULT
                    )
                    win.blit(colored_image, (x, y))
                    pygame.draw.circle(
                        win,
                        C.COLOR["RED"],
                        (center_x, center_y),
                        self.radius + 1,
                        width=2,
                    )
                else:
                    colored_image = state.image_manager.blob_image.copy()
                    colored_image.fill(self.color, special_flags=pygame.BLEND_MULT)
                    win.blit(colored_image, (x, y))
            else:
                if is_best:
                    # Highlighted: yellow fill and red outline
                    pygame.draw.circle(
                        win, C.COLOR["YELLOW"], (center_x, center_y), self.radius
                    )
                    pygame.draw.circle(
                        win,
                        C.COLOR["RED"],
                        (center_x, center_y),
                        self.radius + 1,
                        width=2,
                    )
                else:
                    pygame.draw.circle(
                        win, self.color, (center_x, center_y), self.radius
                    )

    def scan_near_creatures(self) -> list[tuple[Any, int]]:
        cache_key = f"creatures_{self.x}_{self.y}"
        if cache_key in self.scan_cache and self.last_scan_turn == state.turn:
            cached = cast(list[tuple[Any, int]], self.scan_cache[cache_key])
            return cached
        near_list: list[tuple[Any, int]] = []
        for i in range(-state.SCAN_RANGE, state.SCAN_RANGE + 1):
            for j in range(-state.SCAN_RANGE, state.SCAN_RANGE + 1):
                if abs(i) + abs(j) <= state.SCAN_RANGE:
                    x_check = self.x + i
                    y_check = self.y + j
                    if not (
                        0 <= x_check < state.TAILLE_GRID
                        and 0 <= y_check < state.TAILLE_GRID
                    ):
                        continue
                    c = self.grid.grid[x_check][y_check]
                    if c and isinstance(c[0], Blob):
                        dist = abs(i) + abs(j)
                        near_list.append((c[0], dist))
        near_list.sort(key=lambda x: x[1])
        if len(self.scan_cache) >= self.cache_size_limit:
            oldest_key = next(iter(self.scan_cache))
            del self.scan_cache[oldest_key]
        self.scan_cache[cache_key] = list(near_list)
        self.last_scan_turn = state.turn
        return list(near_list)

    def scan_near_food(self) -> list[tuple[Food, int]]:
        cache_key = f"food_{self.x}_{self.y}"
        if cache_key in self.scan_cache and self.last_scan_turn == state.turn:
            cached = cast(list[tuple[Food, int]], self.scan_cache[cache_key])
            return cached
        near_list: list[tuple[Food, int]] = []
        for i in range(-state.SCAN_RANGE, state.SCAN_RANGE + 1):
            for j in range(-state.SCAN_RANGE, state.SCAN_RANGE + 1):
                if abs(i) + abs(j) <= state.SCAN_RANGE:
                    x_check = self.x + i
                    y_check = self.y + j
                    if not (
                        0 <= x_check < state.TAILLE_GRID
                        and 0 <= y_check < state.TAILLE_GRID
                    ):
                        continue
                    c = self.grid.grid[x_check][y_check]
                    if c and isinstance(c[0], Food):
                        dist = abs(i) + abs(j)
                        near_list.append((c[0], dist))
        near_list.sort(key=lambda x: x[1])
        if len(self.scan_cache) >= self.cache_size_limit:
            oldest_key = next(iter(self.scan_cache))
            del self.scan_cache[oldest_key]
        self.scan_cache[cache_key] = list(near_list)
        self.last_scan_turn = state.turn
        return list(near_list)

    def scan_food_density(self) -> list[float]:
        d_NE = calculate_type_density(
            self.grid.grid, self.x, self.y, "NE", C.DENSITY_SCAN_RANGE, Food
        )
        d_NW = calculate_type_density(
            self.grid.grid, self.x, self.y, "NW", C.DENSITY_SCAN_RANGE, Food
        )
        d_SE = calculate_type_density(
            self.grid.grid, self.x, self.y, "SE", C.DENSITY_SCAN_RANGE, Food
        )
        d_SW = calculate_type_density(
            self.grid.grid, self.x, self.y, "SW", C.DENSITY_SCAN_RANGE, Food
        )
        return [max(0.0, min(1.0, v)) for v in [d_NE, d_NW, d_SE, d_SW]]

    def scan_blob_density(self) -> list[float]:
        d_NE = calculate_type_density(
            self.grid.grid, self.x, self.y, "NE", C.DENSITY_SCAN_RANGE, Blob
        )
        d_NW = calculate_type_density(
            self.grid.grid, self.x, self.y, "NW", C.DENSITY_SCAN_RANGE, Blob
        )
        d_SE = calculate_type_density(
            self.grid.grid, self.x, self.y, "SE", C.DENSITY_SCAN_RANGE, Blob
        )
        d_SW = calculate_type_density(
            self.grid.grid, self.x, self.y, "SW", C.DENSITY_SCAN_RANGE, Blob
        )
        return [max(0.0, min(1.0, v)) for v in [d_NE, d_NW, d_SE, d_SW]]

    def moove(self, direction: int) -> int:
        new_x, new_y = self.x, self.y
        if direction == 1:
            new_y = self.y + C.MOOVE_SPEED
        elif direction == 2:
            new_y = self.y - C.MOOVE_SPEED
        elif direction == 3:
            new_x = self.x + C.MOOVE_SPEED
        elif direction == 4:
            new_x = self.x - C.MOOVE_SPEED
        else:
            self.fail += 1
            return 1
        assert state.grid is not None
        # Check borders (no wrapping)
        if not (0 <= new_x < state.TAILLE_GRID and 0 <= new_y < state.TAILLE_GRID):
            return 1
        target_cell = state.grid.grid[new_x][new_y]
        has_blob = any(isinstance(entity, Blob) for entity in target_cell)
        if not has_blob:
            if self in state.grid.grid[self.x][self.y]:
                state.grid.grid[self.x][self.y].remove(self)
            self.x = new_x
            self.y = new_y
            state.grid.grid[self.x][self.y].append(self)
            self.fail = 0
            return 0
        self.fail += 1
        return 1

    def hit_closer(self) -> int:
        if state.turn - self.last_hit_turn < C.HIT_COOLDOWN_TURNS:
            return 1
        near_blob = self.scan_near_creatures()
        if near_blob and near_blob[0][1] <= C.HIT_RANGE:
            target = near_blob[0][0]
            is_kin = hasattr(target, "id") and (
                (self.id in getattr(target, "parent_ids", ()))
                or (target.id in getattr(self, "parent_ids", ()))
            )
            if is_kin:
                self.energy -= C.ATTACK_KIN_PENALTY
                return 1
            # Apply damage and cost, ensure they are applied exactly once
            target.energy -= 5
            self.energy -= C.ATTACK_COST
            if target.energy <= 0:
                target.suicide()
            self.last_hit_turn = state.turn
            return 0
        return 1

    def eat_closer(self) -> int:
        near_food = self.scan_near_food()
        if near_food and near_food[0][1] <= C.EAT_RANGE:
            food_obj = near_food[0][0]
            self.energy += food_obj.amount
            food_obj.suicide()
            self.scan_cache.clear()
            return 0
        return 1

    def reproduce(self) -> None:
        # Old auto-reproduction disabled; reproduction is now triggered by action choice 6
        return

    def try_reproduce_action(self) -> int:
        # Attempt reproduction if there is at least one blob in contact (distance 0)
        if self.energy < 30:
            return 1
        near_blob = self.scan_near_creatures()
        contacts = [
            b
            for (b, d) in near_blob
            if d == 0 and isinstance(b, Blob) and b.energy >= 30
        ]
        if not contacts:
            return 1
        partner: Blob = rd.choice(contacts)
        # Create a child brain by averaging weights and applying occasional mutation
        new_brain = Brain(blob=None)
        for i in range(len(self.brain.weight)):
            new_brain.weight[i] = (self.brain.weight[i] + partner.brain.weight[i]) / 2
            if rd.random() < self.mutation_rate:
                new_brain.weight[i] += np.random.normal(
                    0, C.MUTATION_POWER, new_brain.weight[i].shape
                )
        # Spawn child at Manhattan distance 1 or 2 around parent
        assert state.grid is not None
        # Allow spawn up to Manhattan distance 4 (1..4)
        candidate_offsets: list[tuple[int, int]] = []
        for d in [1, 2, 3, 4]:
            candidate_offsets.extend([(d, 0), (-d, 0), (0, d), (0, -d)])
        rd.shuffle(candidate_offsets)
        for dx, dy in candidate_offsets:
            rx = self.x + dx
            ry = self.y + dy
            if not (0 <= rx < state.TAILLE_GRID and 0 <= ry < state.TAILLE_GRID):
                continue
            cell_entities = state.grid.grid[rx][ry]
            has_blob = any(isinstance(e, Blob) for e in cell_entities)
            if not has_blob:
                # Remove any food in the target cell
                state.grid.grid[rx][ry] = [
                    e for e in cell_entities if not isinstance(e, Food)
                ]
                # Energy for child: 20 + 10% of parents average, capped by MAX_SPAWN_ENERGY
                avg_parents = (self.energy + partner.energy) / 2.0
                spawn_energy = int(min(C.MAX_SPAWN_ENERGY, 20 + 0.1 * avg_parents))
                child = Blob(
                    rx,
                    ry,
                    spawn_energy,
                    grid=self.grid,
                    brain=new_brain,
                    mutation_rate=self.mutation_rate,
                    parent_ids=(self.id, partner.id),
                )
                # Energy cost to parents
                self.energy -= 20
                partner.energy -= 20
                self.grid.instantiate(child)
                self.grid.clear_cache()
                return 0
        return 1

    def main(self) -> None:
        self.energy -= C.ENERGY_DECAY_PER_TURN
        if state.image_manager:
            state.image_manager.rescale(state.CELL_SIZE)
        near_food = self.scan_near_food()
        near_blob = self.scan_near_creatures()

        def norm(val: float, scale: float) -> float:
            if scale == 0:
                return 0.0
            v = val / scale
            if v > 1:
                return 1.0
            if v < -1:
                return -1.0
            return v

        if near_food == []:
            closer_food_vector = [0.0, 0.0, 0.0]
        else:
            closer_food = near_food[0]
            closer_food_vector = [
                norm(dist_x(self, closer_food[0]), max(1, state.SCAN_RANGE)),
                norm(dist_y(self, closer_food[0]), max(1, state.SCAN_RANGE)),
                norm(closer_food[0].amount, 10.0),
            ]
        if near_blob == []:
            closer_blob_vector = [0.0, 0.0, 0.0, norm(self.fail, 10.0)]
            contact_count = 0.0
            contact_avg_energy = 0.0
        else:
            closer_blob = near_blob[0]
            closer_blob_vector = [
                norm(dist_x(self, closer_blob[0]), max(1, state.SCAN_RANGE)),
                norm(dist_y(self, closer_blob[0]), max(1, state.SCAN_RANGE)),
                norm(closer_blob[0].energy, 100.0),
                norm(self.fail, 10.0),
            ]
            # Compute number of contacting blobs and their average energy
            contacts = [b for (b, d) in near_blob if d == 0]
            contact_count = float(len(contacts))
            contact_avg_energy = (
                (sum(b.energy for b in contacts) / contact_count)
                if contact_count > 0
                else 0.0
            )
        entree = (
            closer_food_vector
            + closer_blob_vector
            + self.scan_blob_density()
            + self.scan_food_density()
            + [norm(contact_count, 4.0), norm(contact_avg_energy, 100.0)]
        )
        result = list(self.brain.predict(np.array(entree)))
        self.action_penalties = [
            p * C.ACTION_PENALTY_DECAY for p in self.action_penalties
        ]
        if (
            len(self.recent_actions) == self.recent_actions.maxlen
            and len(set(self.recent_actions)) == 1
        ):
            last_action = self.recent_actions[-1]
            self.action_penalties[last_action] = min(
                C.ACTION_PENALTY_MAX,
                self.action_penalties[last_action] + C.LOOP_PENALTY_INCREMENT,
            )
        energy_norm = max(0.0, min(1.0, self.energy / 100.0))
        temperature = C.SOFTMAX_TEMPERATURE_MIN + (1 - energy_norm) * (
            C.SOFTMAX_TEMPERATURE_MAX - C.SOFTMAX_TEMPERATURE_MIN
        )
        prefs = [
            (r - self.action_penalties[i]) / max(0.01, temperature)
            for i, r in enumerate(result)
        ]
        prefs = [p + rd.uniform(-0.05, 0.05) for p in prefs]
        choice = prefs.index(max(prefs))
        self.consigne_behaviour(choice)
        if choice in [1, 2, 3, 4]:
            self.fail += self.moove(choice)
            self.energy -= 1
        if choice == 0:
            self.fail += self.eat_closer()
        if choice == 5:
            self.fail += self.hit_closer()
        if choice == 6:
            self.fail += self.try_reproduce_action()
        self.recent_actions.append(choice)
        if self.fail > 0:
            self.action_penalties[choice] = min(
                C.ACTION_PENALTY_MAX,
                self.action_penalties[choice] + C.ACTION_FAIL_PENALTY_INCREMENT,
            )
        if self.energy <= 0:
            self.suicide()

    def consigne_behaviour(self, choice: int) -> None:
        if choice in [1, 2, 3, 4]:
            if choice == 1:
                self.behaviour.append("bas")
            if choice == 2:
                self.behaviour.append("haut")
            if choice == 3:
                self.behaviour.append("droite")
            if choice == 4:
                self.behaviour.append("gauche")
        if choice == 0:
            self.behaviour.append("manger")
        if choice == 5:
            self.behaviour.append("taper")
        if choice == 6:
            self.behaviour.append("reproduire")

    def behaviour_percentages(self) -> dict[str, float]:
        total_actions = len(self.behaviour)
        counters: dict[str, float] = {
            k: 0.0
            for k in [
                "manger",
                "taper",
                "bas",
                "haut",
                "droite",
                "gauche",
                "reproduire",
            ]
        }
        if total_actions == 0:
            return counters
        for action in self.behaviour:
            if action in counters:
                counters[action] += 1.0
        return {k: (v * 100.0) / float(total_actions) for k, v in counters.items()}

    def suicide(self) -> None:
        assert state.grid is not None
        if self in state.grid.grid[self.x][self.y]:
            state.grid.grid[self.x][self.y].remove(self)
        if self in self.grid.list_blobs:
            self.grid.list_blobs.remove(self)
        self.scan_cache.clear()


class Grid:
    def __init__(self, list_blobs: list[Any] | None = None) -> None:
        list_blobs = list_blobs or []
        self.list_blobs: list[Any] = list_blobs
        self.oldest_blob: Any = 0
        self.better_blob: Any = 0
        self.grid: list[list[list[Any]]] = [
            [[] for _ in range(state.TAILLE_GRID)] for _ in range(state.TAILLE_GRID)
        ]
        self.scan_cache: dict[str, Any] = {}
        self.cache_turn = -1
        for i in range(state.TAILLE_GRID):
            for j in range(state.TAILLE_GRID):
                rd_spawn = rd.random()
                rd_type = rd.random()
                if rd_spawn <= state.SPAWN_RATE:
                    if rd_type <= state.FOOD_RATE:
                        self.grid[i][j].append(Food(i, j, rd.randint(1, 8)))
                    else:
                        # Only place blob if cell empty of blobs
                        if not any(isinstance(e, Blob) for e in self.grid[i][j]):
                            self.grid[i][j].append(
                                Blob(i, j, C.MAX_SPAWN_ENERGY, grid=self)
                            )

    def instantiate(self, entity: Any) -> None:
        existing_food = [
            e for e in self.grid[entity.x][entity.y] if isinstance(e, Food)
        ]
        if existing_food:
            self.grid[entity.x][entity.y] = [
                e for e in self.grid[entity.x][entity.y] if not isinstance(e, Food)
            ]
            self.grid[entity.x][entity.y].append(entity)
        else:
            self.grid[entity.x][entity.y] = [entity]

    def reset_food(self) -> None:
        for i in range(state.TAILLE_GRID):
            for j in range(state.TAILLE_GRID):
                rd_spawn = rd.random()
                if rd_spawn <= state.RESET_FOOD_RATE:
                    has_food = any(
                        isinstance(entity, Food) for entity in self.grid[i][j]
                    )
                    has_blob = any(
                        isinstance(entity, Blob) for entity in self.grid[i][j]
                    )
                    if not has_food and not has_blob:
                        self.grid[i][j].append(Food(i, j, rd.randint(1, 8)))

    def reset_spawn(self, brain: Any) -> None:
        for i in range(state.TAILLE_GRID):
            for j in range(state.TAILLE_GRID):
                rd_spawn = rd.random()
                if rd_spawn <= state.RESET_SPAWN_RATE:
                    if not any(isinstance(e, Blob) for e in self.grid[i][j]):
                        self.grid[i][j].append(
                            Blob(i, j, C.MAX_SPAWN_ENERGY, grid=self, brain=brain)
                        )

    def reset_map(self) -> None:
        self.list_blobs = []
        self.grid = [
            [[] for _ in range(state.TAILLE_GRID)] for _ in range(state.TAILLE_GRID)
        ]
        for i in range(state.TAILLE_GRID):
            for j in range(state.TAILLE_GRID):
                rd_spawn = rd.random()
                rd_type = rd.random()
                if rd_spawn <= state.SPAWN_RATE:
                    if rd_type <= state.FOOD_RATE:
                        self.grid[i][j].append(Food(i, j, rd.randint(1, 8)))
                    else:
                        if not any(isinstance(e, Blob) for e in self.grid[i][j]):
                            self.grid[i][j].append(
                                Blob(i, j, C.MAX_SPAWN_ENERGY, grid=self)
                            )

    def update_data(self) -> None:
        if self.list_blobs:
            self.oldest_blob = max(self.list_blobs, key=lambda x: len(x.behaviour))
            self.better_blob = max(self.list_blobs, key=lambda x: x.energy)
            self.all_latest_behaviours = [
                blob.behaviour[-1] if blob.behaviour else "none"
                for blob in self.list_blobs
            ]
        else:
            self.oldest_blob = 0
            self.better_blob = 0
            self.all_latest_behaviours = []

    def clear_cache(self) -> None:
        self.scan_cache.clear()
        self.cache_turn = -1
