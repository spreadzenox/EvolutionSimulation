from __future__ import annotations

import gc

import numpy as np
import pygame

from . import constants as C
from .entities import Blob, Grid
from .state import state
from .ui import (
    BackToMenuButton,
    FPSSlider,
    ImageManager,
    LightweightMonitor,
    ParameterSlider,
    StartMenu,
)


def init_pygame() -> None:
    pygame.init()
    state.WIN = pygame.display.set_mode((C.WIDTH + C.WIDTH_INFO, C.HEIGHT))
    pygame.display.set_caption("Evolution Simulation")
    state.FONT = pygame.font.SysFont("comicsans", 16)
    state.FONT_PETIT = pygame.font.SysFont("comicsans", 12)
    state.FONT_GRAND = pygame.font.SysFont("comicsans", 20)


def apply_menu_settings(menu: StartMenu) -> None:
    state.TAILLE_GRID = int(menu.sliders["TAILLE_GRID"].current_val)
    state.BASE_ENERGY = int(menu.sliders["BASE_ENERGY"].current_val)
    state.MUTATION_RATE = menu.sliders["MUTATION_RATE"].current_val
    state.FOOD_RATE = menu.sliders["FOOD_RATE"].current_val
    state.SPAWN_RATE = menu.sliders["SPAWN_RATE"].current_val
    state.SCAN_RANGE = int(menu.sliders["SCAN_RANGE"].current_val)
    state.CELL_SIZE = C.HEIGHT / max(state.TAILLE_GRID, 1)


def pause(run: bool) -> bool:
    return not run


def main() -> None:
    init_pygame()
    clock = pygame.time.Clock()
    state.image_manager = ImageManager()
    start_menu = StartMenu()
    fps_slider = FPSSlider(C.WIDTH + C.WIDTH_INFO - 30 - 240, 150, 240, 20, 1, 120)
    monitor = LightweightMonitor()
    back_btn = BackToMenuButton(10, 10, 50)

    rt_slider_width = 240
    rt_left_x = C.WIDTH + C.WIDTH_INFO - 30 - rt_slider_width
    rt_start_y = 320
    rt_vertical_gap = 12
    rt_slider_height = 20
    realtime_sliders = {
        "MUTATION_RATE": ParameterSlider(
            rt_left_x,
            rt_start_y + 0 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            0.0,
            1.0,
            state.MUTATION_RATE,
            "Mutation",
            0.005,
        ),
        "FOOD_RATE": ParameterSlider(
            rt_left_x,
            rt_start_y + 1 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            0.0,
            1.0,
            state.FOOD_RATE,
            "Food Rate",
            0.01,
        ),
        "RESET_FOOD_RATE": ParameterSlider(
            rt_left_x,
            rt_start_y + 2 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            0.0,
            0.05,
            state.RESET_FOOD_RATE,
            "Food Reset",
            0.001,
        ),
        "SPAWN_RATE": ParameterSlider(
            rt_left_x,
            rt_start_y + 3 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            0.0,
            1.0,
            state.SPAWN_RATE,
            "Spawn Rate",
            0.01,
        ),
        "SCAN_RANGE": ParameterSlider(
            rt_left_x,
            rt_start_y + 4 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            1,
            30,
            state.SCAN_RANGE,
            "Scan Range",
            1,
        ),
        "BASE_ENERGY": ParameterSlider(
            rt_left_x,
            rt_start_y + 5 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            1,
            200,
            state.BASE_ENERGY,
            "Base Energy",
            1,
        ),
    }

    state.running = True
    state.sim_running = True
    state.turn = 0
    state.target_fps = 30
    last_update_time = 0
    update_interval = 1000 // max(state.target_fps, 1)
    memory_cleanup_counter = 0
    state.grid = Grid(list_blobs=[])
    state.grid.update_data()

    while state.running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state.running = False
                break
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                and state.game_state == "simulation"
            ):
                state.sim_running = pause(state.sim_running)
            if state.game_state == "menu":
                for slider in start_menu.sliders.values():
                    slider.handle_event(event)
                menu_action = start_menu.handle_event(event)
                if menu_action == "start":
                    apply_menu_settings(start_menu)
                    if state.image_manager:
                        state.image_manager.rescale(state.CELL_SIZE)
                    state.grid = Grid(list_blobs=[])
                    state.grid.update_data()
                    state.turn = 0
                    for k in (
                        "MUTATION_RATE",
                        "FOOD_RATE",
                        "SPAWN_RATE",
                        "SCAN_RANGE",
                        "BASE_ENERGY",
                    ):
                        realtime_sliders[k].current_val = getattr(state, k)
                    state.game_state = "simulation"
            elif state.game_state == "simulation":
                fps_slider.handle_event(event)
                if back_btn.handle_event(event):
                    state.game_state = "menu"
                for slider in realtime_sliders.values():
                    slider.handle_event(event)

        if state.game_state == "menu":
            pass
        elif state.game_state == "simulation":
            for slider in realtime_sliders.values():
                slider.update()
            state.MUTATION_RATE = realtime_sliders["MUTATION_RATE"].current_val
            state.FOOD_RATE = realtime_sliders["FOOD_RATE"].current_val
            state.RESET_FOOD_RATE = realtime_sliders["RESET_FOOD_RATE"].current_val
            state.SPAWN_RATE = realtime_sliders["SPAWN_RATE"].current_val
            state.SCAN_RANGE = int(realtime_sliders["SCAN_RANGE"].current_val)
            state.BASE_ENERGY = int(realtime_sliders["BASE_ENERGY"].current_val)
            state.target_fps = fps_slider.current_fps
            update_interval = 1000 // max(state.target_fps, 1)
            if current_time - last_update_time >= update_interval:
                if state.sim_running and state.grid is not None:
                    memory_cleanup_counter += 1
                    if memory_cleanup_counter >= 100:
                        gc.collect()
                        memory_cleanup_counter = 0
                    blobs_to_process: list[Blob] = state.grid.list_blobs.copy()
                    for blob in blobs_to_process:
                        if blob in state.grid.list_blobs:
                            blob.main()
                    if state.turn % 4 == 0 and state.turn != 0:
                        state.grid.reset_food()
                    if state.turn % (1000 // C.REPRODUCE_RATE) == 0 and state.turn != 0:
                        blobs_to_reproduce = state.grid.list_blobs.copy()
                        for blob in blobs_to_reproduce:
                            if blob in state.grid.list_blobs:
                                blob.reproduce()
                    monitor.update_stats(state.grid.list_blobs, state.grid)
                    if len(state.grid.list_blobs) <= 0:
                        if state.grid.oldest_blob != 0:
                            with open("oldest.txt", "w") as file:
                                for line in state.grid.oldest_blob.brain.weight:
                                    file.write(np.array2string(line))
                        state.grid.reset_map()
                        state.game_state = "menu"
                    state.turn += 1
                last_update_time = current_time

        assert state.WIN is not None
        state.WIN.fill((0, 0, 0))
        if state.game_state == "menu":
            start_menu.draw(state.WIN)
        elif state.game_state == "simulation":
            state.grid.update_data()
            monitor.draw(state.WIN, C.WIDTH + 30, 60)
            for i in range(state.TAILLE_GRID):
                for j in range(state.TAILLE_GRID):
                    current_object = state.grid.grid[i][j]
                    if current_object:
                        current_object[0].update()
                        current_object[0].draw(state.WIN)
            fps_slider.draw(state.WIN)
            state.current_fps = clock.get_fps()
            if state.FONT_PETIT:
                fps_text = state.FONT_PETIT.render(
                    f"Current FPS: {state.current_fps:.1f}", True, C.COLOR["ORANGE"]
                )
                state.WIN.blit(fps_text, (C.WIDTH + C.WIDTH_INFO - 30 - 240, 100))
            for _, slider in realtime_sliders.items():
                slider.draw(state.WIN)
            back_btn.draw(state.WIN)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
