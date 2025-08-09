from __future__ import annotations

import pygame

from . import constants as C
from .state import state


class ImageManager:
    def __init__(self) -> None:
        self.blob_image: pygame.Surface | None = None
        self.food_image: pygame.Surface | None = None
        self.blob_original: pygame.Surface | None = None
        self.food_original: pygame.Surface | None = None
        self.last_cell_size: int = -1
        self.load_images()

    def load_images(self) -> None:
        try:
            self.blob_original = pygame.image.load("blob.png").convert_alpha()
            self.food_original = pygame.image.load("food.png").convert_alpha()
            self.rescale(state.CELL_SIZE)
        except Exception:
            self.blob_image = None
            self.food_image = None

    def rescale(self, cell_size: float) -> None:
        try:
            target = max(1, int(cell_size))
            if target == self.last_cell_size:
                return
            if self.blob_original is not None:
                self.blob_image = pygame.transform.scale(
                    self.blob_original, (target, target)
                )
            if self.food_original is not None:
                self.food_image = pygame.transform.scale(
                    self.food_original, (target, target)
                )
            self.last_cell_size = target
        except Exception:
            pass


class ParameterSlider:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        min_val: float,
        max_val: float,
        current_val: float,
        name: str,
        step: float = 1.0,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.name = name
        self.step = step
        self.dragging = False
        self.slider_rect = pygame.Rect(
            x + (current_val - min_val) / (max_val - min_val) * width, y, 10, height
        )

    def set_position(
        self,
        x: int | None = None,
        y: int | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        relative_x = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        knob_x = self.x + int(relative_x * self.width)
        self.slider_rect = pygame.Rect(knob_x, self.y, 10, self.height)

    def block_height(self) -> int:
        text_h = state.FONT_PETIT.get_height() if state.FONT_PETIT else 12
        return int(30 + self.height + 10 + text_h + 20)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.slider_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.x
            rel_x = max(0, min(self.width, rel_x))
            self.current_val = self.min_val + (rel_x / self.width) * (
                self.max_val - self.min_val
            )
            self.current_val = round(self.current_val / self.step) * self.step
            self.slider_rect.x = self.x + rel_x

    def update(self) -> None:
        # no-op for now
        return None

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(
            surface, C.COLOR["DARK_GREY"], (self.x, self.y, self.width, self.height)
        )
        pygame.draw.rect(surface, C.COLOR["GREEN"], self.slider_rect)
        if not state.FONT_PETIT or not state.FONT:
            return
        text = state.FONT_PETIT.render(
            f"{self.name}: {self.current_val}", True, C.COLOR["WHITE"]
        )
        surface.blit(text, (self.x, self.y - 30))
        min_text = state.FONT_PETIT.render(str(self.min_val), True, C.COLOR["WHITE"])
        max_text = state.FONT_PETIT.render(str(self.max_val), True, C.COLOR["WHITE"])
        surface.blit(min_text, (self.x, self.y + self.height + 10))
        surface.blit(max_text, (self.x + self.width - 40, self.y + self.height + 10))


class StartMenu:
    def __init__(self) -> None:
        self.slider_width = 400
        self.slider_x = (C.WIDTH + C.WIDTH_INFO) // 2 - self.slider_width // 2
        self.sliders: dict[str, ParameterSlider] = {
            "TAILLE_GRID": ParameterSlider(
                self.slider_x,
                0,
                self.slider_width,
                30,
                20,
                800,
                state.TAILLE_GRID,
                "Grid Size",
                10,
            ),
            "BASE_ENERGY": ParameterSlider(
                self.slider_x,
                0,
                self.slider_width,
                30,
                1,
                200,
                state.MAX_SPAWN_ENERGY,
                "Max spawn energy",
                1,
            ),
            "MUTATION_RATE": ParameterSlider(
                self.slider_x,
                0,
                self.slider_width,
                30,
                0.0,
                1.0,
                state.MUTATION_RATE,
                "Mutation Rate",
                0.005,
            ),
            "FOOD_RATE": ParameterSlider(
                self.slider_x,
                0,
                self.slider_width,
                30,
                0.0,
                1.0,
                state.FOOD_RATE,
                "Food Rate",
                0.01,
            ),
            "SPAWN_RATE": ParameterSlider(
                self.slider_x,
                0,
                self.slider_width,
                30,
                0.0,
                1.0,
                state.SPAWN_RATE,
                "Spawn Rate",
                0.01,
            ),
            "SCAN_RANGE": ParameterSlider(
                self.slider_x,
                0,
                self.slider_width,
                30,
                1,
                30,
                state.SCAN_RANGE,
                "Scan Range",
                1,
            ),
        }
        self.slider_keys = [
            "TAILLE_GRID",
            "BASE_ENERGY",
            "MUTATION_RATE",
            "FOOD_RATE",
            "SPAWN_RATE",
            "SCAN_RANGE",
        ]
        self.start_button_rect = pygame.Rect(
            (C.WIDTH + C.WIDTH_INFO) // 2 - 100, 620, 200, 50
        )

    def handle_event(self, event: pygame.event.Event) -> str | None:
        # Use scaled rect for hit-testing to match draw coordinates
        scale_x = state.SCALE_X or 1.0
        scale_y = state.SCALE_Y or 1.0
        btn_w = int(200 * scale_x)
        btn_h = int(50 * scale_y)
        btn_x = int(((C.WIDTH + C.WIDTH_INFO) // 2 - 100) * scale_x)
        btn_y = int(620 * scale_y)
        scaled_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        if event.type == pygame.MOUSEBUTTONDOWN and scaled_rect.collidepoint(event.pos):
            return "start"
        return None

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        if not state.FONT_GRAND or not state.FONT:
            return
        scale_x = state.SCALE_X or 1.0
        scale_y = state.SCALE_Y or 1.0
        title = state.FONT_GRAND.render("EVOLUTION SIMULATION", True, C.COLOR["CYAN"])
        surface.blit(title, (int((C.WIDTH // 2 - 150) * scale_x), int(30 * scale_y)))
        subtitle = state.FONT.render("Parameters", True, C.COLOR["WHITE"])
        surface.blit(subtitle, (int((C.WIDTH // 2 - 70) * scale_x), int(60 * scale_y)))
        current_y = int(140 * scale_y)
        for key in self.slider_keys:
            slider = self.sliders[key]
            slider.set_position(
                int(self.slider_x * scale_x),
                current_y,
                int(self.slider_width * scale_x),
                int(30 * scale_y),
            )
            slider.draw(surface)
            current_y += slider.block_height()
        # Scale start button
        btn_w = int(200 * scale_x)
        btn_h = int(50 * scale_y)
        btn_x = int(((C.WIDTH + C.WIDTH_INFO) // 2 - 100) * scale_x)
        btn_y = int(620 * scale_y)
        self.start_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, C.COLOR["GREEN"], self.start_button_rect)
        pygame.draw.rect(surface, C.COLOR["WHITE"], self.start_button_rect, 2)
        start_text = (
            state.FONT_GRAND.render("START", True, C.COLOR["BLACK"])
            if state.FONT_GRAND
            else None
        )
        if start_text:
            text_rect = start_text.get_rect(center=self.start_button_rect.center)
            surface.blit(start_text, text_rect)


class BackToMenuButton:
    def __init__(self, x: int, y: int, size: int = 50) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)

    def _scaled_rect(self) -> pygame.Rect:
        scale_x = state.SCALE_X or 1.0
        scale_y = state.SCALE_Y or 1.0
        return pygame.Rect(
            int(self.x * scale_x),
            int(self.y * scale_y),
            int(self.size * scale_x),
            int(self.size * scale_y),
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and self._scaled_rect().collidepoint(
            event.pos
        ):
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        scale_x = state.SCALE_X or 1.0
        scale_y = state.SCALE_Y or 1.0
        # Recompute rect with scaling for rendering
        scaled_rect = self._scaled_rect()
        bg_color = C.COLOR["DARK_GREY"]
        pygame.draw.rect(surface, bg_color, scaled_rect)
        border_color = C.COLOR["LIGHT_GREY"]
        pygame.draw.rect(surface, border_color, scaled_rect, 2)
        center_x = scaled_rect.x + scaled_rect.width // 2
        center_y = scaled_rect.y + scaled_rect.height // 2
        points = [
            (center_x + int(8 * scale_x), center_y - int(8 * scale_y)),
            (center_x - int(8 * scale_x), center_y),
            (center_x + int(8 * scale_x), center_y + int(8 * scale_y)),
        ]
        pygame.draw.polygon(surface, C.COLOR["ORANGE"], points)
        if state.FONT_PETIT:
            text_surface = state.FONT_PETIT.render("MENU", True, C.COLOR["WHITE"])
            text_rect = text_surface.get_rect(
                center=(center_x, center_y + int(25 * scale_y))
            )
            surface.blit(text_surface, text_rect)


class PauseButton:
    def __init__(self, x: int, y: int, width: int = 120, height: int = 40) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def _scaled_rect(self) -> pygame.Rect:
        scale_x = state.SCALE_X or 1.0
        scale_y = state.SCALE_Y or 1.0
        return pygame.Rect(
            int(self.x * scale_x),
            int(self.y * scale_y),
            int(self.width * scale_x),
            int(self.height * scale_y),
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and self._scaled_rect().collidepoint(
            event.pos
        ):
            return True
        return False

    def draw(self, surface: pygame.Surface, is_running: bool) -> None:
        scaled_rect = self._scaled_rect()
        bg = C.COLOR["ORANGE"] if is_running else C.COLOR["GREEN"]
        pygame.draw.rect(surface, bg, scaled_rect)
        pygame.draw.rect(surface, C.COLOR["WHITE"], scaled_rect, 2)
        label = "PAUSE" if is_running else "RUN"
        if state.FONT:
            text_surface = state.FONT.render(label, True, C.COLOR["BLACK"])
            text_rect = text_surface.get_rect(center=scaled_rect.center)
            surface.blit(text_surface, text_rect)


class FPSSlider:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        min_fps: int = 1,
        max_fps: int = 120,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_fps = min_fps
        self.max_fps = max_fps
        self.current_fps = 30
        self.dragging = False
        self.slider_rect = pygame.Rect(
            x + (self.current_fps - min_fps) / (max_fps - min_fps) * width,
            y,
            10,
            height,
        )

    def set_position(
        self, x: int, y: int, width: int | None = None, height: int | None = None
    ) -> None:
        self.x = x
        self.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        relative_x = (self.current_fps - self.min_fps) / (self.max_fps - self.min_fps)
        knob_x = self.x + int(relative_x * self.width)
        self.slider_rect = pygame.Rect(knob_x, self.y, max(8, 10), self.height)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and self.slider_rect.collidepoint(
            event.pos
        ):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.x
            rel_x = max(0, min(self.width, rel_x))
            self.current_fps = self.min_fps + (rel_x / self.width) * (
                self.max_fps - self.min_fps
            )
            self.current_fps = int(self.current_fps)
            self.slider_rect.x = self.x + rel_x

    def draw(self, surface: pygame.Surface) -> None:
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        knob_rect = pygame.Rect(
            self.slider_rect.x,
            self.slider_rect.y,
            self.slider_rect.width,
            self.slider_rect.height,
        )
        pygame.draw.rect(surface, C.COLOR["DARK_GREY"], bg_rect)
        pygame.draw.rect(surface, C.COLOR["GREEN"], knob_rect)
        if state.FONT_PETIT:
            text = state.FONT_PETIT.render(
                f"FPS: {self.current_fps}", True, C.COLOR["WHITE"]
            )
            surface.blit(text, (bg_rect.x, bg_rect.y - 20))
            min_text = state.FONT_PETIT.render(
                str(self.min_fps), True, C.COLOR["WHITE"]
            )
            max_text = state.FONT_PETIT.render(
                str(self.max_fps), True, C.COLOR["WHITE"]
            )
            surface.blit(min_text, (bg_rect.x, bg_rect.y + bg_rect.height + 5))
            surface.blit(
                max_text,
                (bg_rect.x + bg_rect.width - 20, bg_rect.y + bg_rect.height + 5),
            )


class LightweightMonitor:
    def __init__(self) -> None:
        self.behaviour_counts = {
            "manger": 0,
            "taper": 0,
            "bas": 0,
            "haut": 0,
            "droite": 0,
            "gauche": 0,
        }
        self.energy_stats: dict[str, int] = {"min": 0, "max": 0, "avg": 0}
        self.population_history: list[int] = []
        self.food_count = 0

    def update_stats(self, blobs: list, grid_obj: object) -> None:
        if not blobs:
            return
        energies = [blob.energy for blob in blobs]
        self.energy_stats = {
            "min": min(energies),
            "max": max(energies),
            "avg": sum(energies) // len(energies),
        }
        self.behaviour_counts = {k: 0 for k in self.behaviour_counts}
        for blob in blobs:
            if blob.behaviour:
                last_behaviour = blob.behaviour[-1]
                if last_behaviour in self.behaviour_counts:
                    self.behaviour_counts[last_behaviour] += 1
        self.food_count = 0
        if hasattr(grid_obj, "grid"):
            from .entities import Food  # local import to avoid cycles

            for i in range(state.TAILLE_GRID):
                for j in range(state.TAILLE_GRID):
                    for entity in grid_obj.grid[i][j]:
                        if isinstance(entity, Food):
                            self.food_count += 1
        self.population_history.append(len(blobs))
        if len(self.population_history) > 50:
            self.population_history.pop(0)

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        if not state.FONT or not state.FONT_GRAND:
            return
        scale_x = state.SCALE_X or 1.0
        scale_y = state.SCALE_Y or 1.0
        sx = int(x * scale_x)
        sy = int(y * scale_y)
        title = state.FONT_GRAND.render("SIMULATION MONITOR", True, C.COLOR["CYAN"])
        surface.blit(title, (sx, sy))
        sy += int(30 * scale_y)
        stats_text = [
            f"Turn: {state.turn}",
            f"Blobs alive: {len(state.grid.list_blobs) if state.grid else 0}",
            f"Food: {self.food_count}",
            f"Target FPS: {state.target_fps}",
            f"Current FPS: {state.current_fps:.1f}",
        ]
        for i, text in enumerate(stats_text):
            color = C.COLOR["WHITE"] if i < 3 else C.COLOR["ORANGE"]
            rendered = state.FONT.render(text, True, color)
            surface.blit(rendered, (sx, sy + int(i * 20 * scale_y)))
        sy += int(120 * scale_y)
        energy_title = state.FONT.render("ENERGY", True, C.COLOR["GREEN"])
        surface.blit(energy_title, (sx, sy))
        sy += int(25 * scale_y)
        for key in ["min", "max", "avg"]:
            rendered = (
                state.FONT_PETIT.render(
                    f"{key.capitalize()}: {self.energy_stats[key]}",
                    True,
                    C.COLOR["WHITE"],
                )
                if state.FONT_PETIT
                else None
            )
            if rendered:
                surface.blit(rendered, (sx, sy))
                sy += int(18 * scale_y)
        sy += int(10 * scale_y)
        behaviour_title = state.FONT.render("BEHAVIOURS", True, C.COLOR["PURPLE"])
        surface.blit(behaviour_title, (sx, sy))
        sy += int(25 * scale_y)
        for behaviour, count in self.behaviour_counts.items():
            if count > 0 and state.FONT_PETIT:
                text = f"{behaviour}: {count}"
                color = C.COLOR["YELLOW"] if count > 10 else C.COLOR["WHITE"]
                rendered = state.FONT_PETIT.render(text, True, color)
                surface.blit(rendered, (sx, sy))
                sy += int(18 * scale_y)
        sy += int(20 * scale_y)
        if self.population_history and state.FONT and state.grid is not None:
            pop_title = state.FONT.render("POPULATION", True, C.COLOR["BLUE"])
            surface.blit(pop_title, (sx, sy))
            sy += int(25 * scale_y)
            graph_width = int(200 * scale_x)
            graph_height = int(100 * scale_y)
            graph_x = sx
            graph_y = sy
            pygame.draw.rect(
                surface,
                C.COLOR["DARK_GREY"],
                (graph_x, graph_y, graph_width, graph_height),
            )
            if len(self.population_history) > 1:
                max_pop = max(self.population_history)
                points = []
                for i, pop in enumerate(self.population_history):
                    x_pos = graph_x + int(
                        (i / (len(self.population_history) - 1)) * graph_width
                    )
                    y_pos = (
                        graph_y + int(graph_height - (pop / max_pop) * graph_height)
                        if max_pop
                        else graph_y + graph_height
                    )
                    points.append((x_pos, y_pos))
                if len(points) > 1:
                    pygame.draw.lines(surface, C.COLOR["GREEN"], False, points, 2)
            sy += graph_height + int(20 * scale_y)
